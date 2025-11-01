"""
Cross-cutting safeguards & controls for Phase 6.

Implements:
 - multi-objective fitness computation with hard-constraint checking
 - Pareto front selection utilities
 - LTMManager: protected vertices, promotion policy, versioned mapping, snapshots & rollback
 - mutation operators: bit-flip, jump, adapter noise with mutation caps
 - lightweight dashboard aggregator (population health, PIP activity, alarms)

Keep lightweight and dependency-free (numpy + stdlib).
"""
from typing import Dict, List, Tuple, Any, Optional
import json
import os
import time
import copy
import numpy as np

# Default fitness weights (tuneable)
DEFAULT_WEIGHTS = {
    "coherence": 0.35,
    "factuality": 0.35,
    "novelty": 0.15,
    "analogy": 0.1,
    "alignment": 0.05,
    "toxicity": -0.5,  # toxicity is a penalty (higher toxicity lowers fitness)
}


def compute_fitness(scores: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> float:
    """
    Compute weighted fitness from a metric dict. Scores assumed in [0,1].
    If toxicity present, it's treated as penalty (weight negative).
    """
    w = weights or DEFAULT_WEIGHTS
    fitness = 0.0
    for k, weight in w.items():
        val = float(scores.get(k, 0.0))
        fitness += weight * val
    return float(fitness)


def check_hard_constraints(scores: Dict[str, float], floors: Optional[Dict[str, float]] = None) -> Tuple[bool, List[str]]:
    """
    Enforce hard floors for selection. Returns (pass, failed_keys)
    Example floors: {"coherence": 0.7, "factuality": 0.65}
    """
    floors = floors or {"coherence": 0.7}
    failed = []
    for k, threshold in floors.items():
        if float(scores.get(k, 0.0)) < float(threshold):
            failed.append(k)
    return (len(failed) == 0, failed)


def pareto_front(items: List[Tuple[Any, Dict[str, float]]], objectives: List[str]) -> List[Any]:
    """
    Compute Pareto front (non-dominated) given items list of (obj, metrics).
    Objectives are assumed to be maximized. Return list of objs on Pareto front.
    Complexity: O(n^2) acceptable for small populations.
    """
    objs = [it[0] for it in items]
    metrics = [it[1] for it in items]
    n = len(items)
    dominated = [False] * n
    for i in range(n):
        if dominated[i]:
            continue
        for j in range(n):
            if i == j:
                continue
            better_or_equal = True
            strictly_better = False
            for key in objectives:
                vi = float(metrics[i].get(key, 0.0))
                vj = float(metrics[j].get(key, 0.0))
                if vj < vi:
                    better_or_equal = False
                    break
                if vj > vi:
                    strictly_better = True
            if better_or_equal and strictly_better:
                dominated[i] = True
                break
    return [objs[i] for i in range(n) if not dominated[i]]


class LTMManager:
    """
    Long-term memory manager for vertex mappings / memes.
    - protected_vertices: set kept locked unless human-approved
    - versioned_map: list of snapshots (timestamped)
    - promotion policy: require min_generations OR human_approval to promote
    """
    def __init__(self, path: str = "ltm_map.json", backups_dir: str = "ltm_backups", protected: Optional[List[int]] = None):
        self.path = path
        self.backups_dir = backups_dir
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)
        self.protected_vertices = set(protected or [])
        # mapping: concept -> vertex_id
        self.mapping: Dict[str, int] = {}
        self.versions: List[Dict[str, Any]] = []
        # load if exists
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.mapping = data.get("mapping", {})
                self.versions = data.get("versions", [])
            except Exception:
                self.mapping = {}
                self.versions = []

    def snapshot(self, label: Optional[str] = None):
        ts = int(time.time())
        version = {"ts": ts, "label": label or "", "mapping": copy.deepcopy(self.mapping)}
        self.versions.append(version)
        # save to disk and backup
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"mapping": self.mapping, "versions": self.versions}, f, indent=2)
        backup = os.path.join(self.backups_dir, f"ltm_snapshot_{ts}.json")
        with open(backup, "w", encoding="utf-8") as f:
            json.dump(version, f, indent=2)
        return backup

    def rollback_to(self, backup_path: str) -> bool:
        if not os.path.exists(backup_path):
            return False
        with open(backup_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.mapping = data.get("mapping", {})
        # record rollback as version
        self.snapshot(label=f"rollback_from_{os.path.basename(backup_path)}")
        return True

    def protect_vertex(self, vid: int):
        self.protected_vertices.add(int(vid))

    def unprotect_vertex(self, vid: int):
        self.protected_vertices.discard(int(vid))

    def can_modify_vertex(self, vid: int) -> bool:
        return int(vid) not in self.protected_vertices

    def propose_promote(self, concept: str, vid: int, passed_auto: bool, human_approved: bool, generations_survived: int, min_gens: int = 3) -> bool:
        """
        Promotion policy:
         - If vertex is protected and mapping exists, do not overwrite unless human_approved
         - Promote when passed_auto AND (generations_survived >= min_gens OR human_approved)
        Returns True if promoted (written to mapping).
        """
        if int(vid) in self.protected_vertices and not human_approved:
            return False
        if not passed_auto and not human_approved:
            return False
        if generations_survived >= min_gens or human_approved:
            self.mapping[concept] = int(vid)
            self.snapshot(label=f"promote_{concept}_{vid}")
            return True
        return False


def bitflip_mutation(hypercube_mask: List[int], rng: Optional[np.random.RandomState] = None, flip_prob: float = 0.01, max_flips: int = 2) -> List[int]:
    """
    Flip up to max_flips bits with independent flip_prob, return new mask.
    """
    rng = rng or np.random.RandomState()
    mask = list(hypercube_mask)
    indices = list(range(len(mask)))
    rng.shuffle(indices)
    flips = 0
    for i in indices:
        if flips >= max_flips:
            break
        if rng.rand() < flip_prob:
            mask[i] = 1 - mask[i]
            flips += 1
    return mask


def jump_mutation(hypercube_mask: List[int], rng: Optional[np.random.RandomState] = None, jump_bits: int = 3) -> List[int]:
    """
    Rare jump mutation flipping jump_bits randomly (PIP-only).
    """
    rng = rng or np.random.RandomState()
    mask = list(hypercube_mask)
    n = len(mask)
    idxs = rng.choice(n, size=min(jump_bits, n), replace=False)
    for i in idxs:
        mask[i] = 1 - mask[i]
    return mask


def adapter_noise_mutation(adapters: np.ndarray, rng: Optional[np.random.RandomState] = None, scale: float = 0.02, mutation_cap: float = 0.2) -> np.ndarray:
    """
    Add gaussian noise to adapter vector, enforce L2 mutation cap.
    """
    rng = rng or np.random.RandomState()
    noise = rng.randn(*adapters.shape).astype(np.float32) * scale
    orig = adapters.copy()
    new = orig + noise
    l2 = np.linalg.norm(new - orig)
    if l2 > mutation_cap:
        new = orig + (new - orig) * (mutation_cap / (l2 + 1e-12))
    return new


class Dashboard:
    """
    Lightweight aggregator to compute monitoring panels.
    Accepts population list of dicts: {"id", "fitness", "scores", "meta"} and memetic monitor.
    """
    def __init__(self, memetic_monitor = None):
        self.memetic_monitor = memetic_monitor

    def population_health(self, population: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not population:
            return {"average_fitness": 0.0, "best_fitness": 0.0, "diversity": 0.0}
        fits = [p.get("fitness", 0.0) for p in population]
        avg = float(np.mean(fits))
        best = float(np.max(fits))
        # diversity as std of adapter vectors if present
        adapters = [p.get("meta", {}).get("adapters") for p in population if p.get("meta", {}).get("adapters") is not None]
        if adapters:
            mats = np.vstack(adapters)
            diversity = float(np.mean(np.std(mats, axis=0)))
        else:
            diversity = float(np.std(fits))
        return {"average_fitness": avg, "best_fitness": best, "diversity": diversity, "size": len(population)}

    def pip_activity(self, population: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not population:
            return {"pip_percent": 0.0, "pip_acceptance_rate": 0.0}
        pip_count = sum(1 for p in population if p.get("meta", {}).get("pip", False))
        pip_percent = pip_count / max(1, len(population))
        pip_accept = 0.0
        if self.memetic_monitor:
            pip_accept = self.memetic_monitor.pip_acceptance_rate()
        return {"pip_percent": pip_percent, "pip_acceptance_rate": pip_accept}

    def safety_metrics(self, recent_flags: List[Dict[str, Any]]) -> Dict[str, Any]:
        # recent_flags: list of {"type": "hallucination"/"toxicity", "count": int} entries
        totals = {}
        for f in recent_flags:
            totals[f["type"]] = totals.get(f["type"], 0) + f.get("count", 0)
        return totals

    def alarms(self, entropy: float, thresholds: Dict[str, float]) -> List[str]:
        out = []
        if entropy >= thresholds.get("drift", 0.7):
            out.append(f"DRIFT alarm: entropy {entropy:.3f} >= {thresholds.get('drift')}")
        return out
