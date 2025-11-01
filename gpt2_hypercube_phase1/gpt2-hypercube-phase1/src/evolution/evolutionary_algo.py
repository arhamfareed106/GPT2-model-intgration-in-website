"""
Evolutionary algorithm with memetic local search and PIP creative mode.
Includes safeguards and an append-only audit log.
"""
import os
import json
import time
import copy
import numpy as np
from typing import List, Callable, Dict, Any, Tuple
from .genome import Genome
from .agent import Agent
from .evaluator import Evaluator

AUDIT_DIR = "evolution_audit"
os.makedirs(AUDIT_DIR, exist_ok=True)


def _audit(log: Dict[str, Any]):
    path = os.path.join(AUDIT_DIR, "audit.logl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": int(time.time()), **log}) + "\n")


def init_population(pop_size: int, adapter_dim: int, concept_dim: int, hypercube_n: int, seed: int = 42) -> List[Genome]:
    rng = np.random.RandomState(seed)
    pops = []
    for _ in range(pop_size):
        adapters = rng.randn(adapter_dim).astype(np.float32) * 0.02
        bias = rng.randn(concept_dim).astype(np.float32) * 0.01
        mask = [int(b) for b in rng.randint(0, 2, size=(hypercube_n,))]
        meta = {"lambda_con": float(rng.uniform(0.0, 1.0)), "mutation_rate": 0.1, "pip": bool(rng.rand() > 0.9)}
        pops.append(Genome(adapters=adapters, concept_bias=bias, hypercube_mask=mask, meta=meta))
    _audit({"evt": "init_population", "pop_size": pop_size, "adapter_dim": adapter_dim})
    return pops


def crossover(a: Genome, b: Genome, rng: np.random.RandomState) -> Genome:
    # simple uniform crossover on adapters and bias
    mask = rng.rand(len(a.adapters)) > 0.5
    child_adapters = a.adapters.copy()
    child_adapters[~mask] = b.adapters[~mask]
    maskb = rng.rand(len(a.concept_bias)) > 0.5
    child_bias = a.concept_bias.copy()
    child_bias[~maskb] = b.concept_bias[~maskb]
    # hypercube mask: crossover per-bit
    hm = [a.hypercube_mask[i] if rng.rand() > 0.5 else b.hypercube_mask[i] for i in range(len(a.hypercube_mask))]
    # meta: inherit lambda_con average, mutation_rate average, pip if either has pip sometimes
    meta = {"lambda_con": float((a.meta.get("lambda_con", 0.5) + b.meta.get("lambda_con", 0.5)) / 2.0),
            "mutation_rate": float((a.meta.get("mutation_rate", 0.1) + b.meta.get("mutation_rate", 0.1)) / 2.0),
            "pip": bool(rng.rand() < (0.2 + 0.6 * (1 if a.meta.get("pip", False) or b.meta.get("pip", False) else 0)))}
    child = Genome(adapters=child_adapters, concept_bias=child_bias, hypercube_mask=hm, meta=meta)
    _audit({"evt": "crossover", "parents": [a.id, b.id], "child": child.id})
    return child


def mutate(gen: Genome, rng: np.random.RandomState, mutation_cap: float = 0.2):
    """
    Mutate adapters, bias, and hypercube mask.
    mutation_cap limits cumulative adapter L2 change per generation.
    PIP mode increases mutation ranges.
    """
    rate = gen.meta.get("mutation_rate", 0.1)
    pip = bool(gen.meta.get("pip", False))
    # adapter mutation
    scale = 0.05 * (2.0 if pip else 1.0)
    noise = rng.randn(*gen.adapters.shape).astype(np.float32) * scale * rate
    # enforce mutation cap
    orig = gen.adapters.copy()
    gen.adapters += noise
    l2 = np.linalg.norm(gen.adapters - orig)
    if l2 > mutation_cap:
        gen.adapters = orig + (gen.adapters - orig) * (mutation_cap / (l2 + 1e-12))
    # bias mutation
    gen.concept_bias += rng.randn(*gen.concept_bias.shape).astype(np.float32) * 0.02 * rate * (2.0 if pip else 1.0)
    # hypercube mask flips: with small prob flip some bits; pip allows multi-bit flips
    flip_prob = 0.02 * (5.0 if pip else 1.0)
    for i in range(len(gen.hypercube_mask)):
        if rng.rand() < flip_prob:
            gen.hypercube_mask[i] = 1 - gen.hypercube_mask[i]
    _audit({"evt": "mutate", "id": gen.id, "pip": pip})


def tournament_select(pop: List[Tuple[Genome, float]], k: int, rng: np.random.RandomState) -> Genome:
    # pick k random, return best by score
    idx = rng.choice(len(pop), size=min(k, len(pop)), replace=False)
    best = None
    best_score = -1.0
    for i in idx:
        g, sc = pop[i]
        if sc > best_score:
            best = g
            best_score = sc
    return best.copy()


def memetic_local_search(gen: Genome, agent_factory: Callable[[Genome], Agent], evaluator: Evaluator, prompt: str, budget: int = 5, rng=None):
    """
    Simple local search: try small perturbations to adapters and accept improvements.
    budget: number of small trials
    """
    rng = rng or np.random.RandomState()
    best = gen.copy
