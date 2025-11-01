"""
Phase 6 evaluation metrics: coherence (placeholder), factuality via vectordb matching,
novelty via embedding distance, stability (hypercube drift), and memory fidelity.
"""
from typing import List, Dict, Any, Optional
import numpy as np
from collections import Counter
import math


def coherence_score(human_ratings: List[float]) -> float:
    """Aggregate human ratings in [0,1]."""
    if not human_ratings:
        return 0.0
    return float(max(0.0, min(1.0, sum(human_ratings) / len(human_ratings))))


def factuality_score(output: str, query_vec: Optional[np.ndarray], vectordb, top_k: int = 5, sim_thresh: float = 0.6) -> float:
    """
    Estimate factuality by checking whether top-k retrieved provenance items have similarity above threshold.
    If no vectordb or query_vec provided, returns 0.5 (unknown).
    """
    if vectordb is None or query_vec is None:
        return 0.5
    res = vectordb.query(query_vec, top_k=top_k)
    if not res:
        return 0.0
    sims = [r["score"] for r in res]
    return float(sum(1 for s in sims if s >= sim_thresh) / max(1, len(sims)))


def novelty_score(query_vec: np.ndarray, vectordb, top_k: int = 50) -> float:
    """
    Novelty measured as average distance to nearest neighbors in vectordb.
    Higher distance -> more novel (normalized to [0,1]).
    """
    if vectordb is None or query_vec is None:
        return 0.5
    res = vectordb.query(query_vec, top_k=top_k)
    if not res:
        return 1.0
    sims = [r["score"] for r in res]
    # similarity in [-1,1] for cosine -> map to novelty = 1 - mean(sim)
    mean_sim = float(sum(sims) / len(sims))
    return float(max(0.0, min(1.0, 1.0 - mean_sim)))


def hypercube_path_entropy(paths: List[List[int]]) -> float:
    """
    Compute entropy over vertex frequencies as a proxy for stability/drift.
    Higher entropy => more drift/less stability.
    """
    if not paths:
        return 0.0
    flat = [v for p in paths for v in p]
    if not flat:
        return 0.0
    counts = Counter(flat)
    total = sum(counts.values())
    ent = 0.0
    for c in counts.values():
        p = c / total
        ent -= p * math.log(p + 1e-12)
    # normalize by log(unique) to bring to [0,1]
    max_ent = math.log(len(counts) + 1e-12)
    return float(ent / (max_ent + 1e-12))


def memory_fidelity(expected_paths: List[List[int]], recalled_paths: List[List[int]]) -> float:
    """
    Fraction of expected path items recovered in recalled paths (averaged).
    """
    if not expected_paths:
        return 1.0
    tot = 0.0
    n = 0
    for exp, rec in zip(expected_paths, recalled_paths):
        if not exp:
            continue
        hit = sum(1 for v in exp if v in rec)
        tot += hit / max(1, len(exp))
        n += 1
    return float(tot / n) if n > 0 else 0.0
