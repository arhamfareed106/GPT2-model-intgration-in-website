"""
Fitness suite that scores outputs along multiple axes.
This is intentionally lightweight / pluggable: replace with real evaluators.
"""
from typing import Dict
import numpy as np


def _norm(x, lo=0.0, hi=1.0):
    if np.isnan(x) or np.isinf(x):
        return 0.0
    return float(max(lo, min(hi, x)))


class Evaluator:
    def __init__(self):
        pass

    def score(self, output: str, reference: str = "") -> Dict[str, float]:
        """
        Returns scores in [0,1] for coherence, factuality, novelty, analogy, alignment.
        Simple heuristics:
          - coherence: penalize very short outputs and huge token repetition
          - factuality: if reference non-empty, measure overlap ratio; else 0.5
          - novelty: length normalized by 50 tokens
          - analogy: placeholder random-ish based on hashing
          - alignment: penalize bad tokens (placeholder)
        """
        # basic tokenization
        toks = output.split()
        L = len(toks)
        # coherence: prefer moderate length and token variety
        uniq = len(set(toks))
        coh = _norm((uniq / max(1, L)) * (min(L, 50) / 50.0))
        # factuality via overlap if reference provided
        if reference:
            ref_toks = set(reference.split())
            overlap = len(ref_toks.intersection(set(toks)))
            factual = _norm(overlap / max(1, len(ref_toks)))
        else:
            factual = 0.5
        novelty = _norm(min(1.0, L / 50.0))
        # analogy: deterministic pseudo-random from string hash
        analogy = _norm(((hash(output) % 100) / 100.0))
        # alignment: penalize presence of "<BAD>" token (placeholder)
        alignment = 0.0 if "<BAD>" in output else 0.9
        return {
            "coherence": coh,
            "factuality": factual,
            "novelty": novelty,
            "analogy": analogy,
            "alignment": alignment,
        }

    def aggregate(self, scores: Dict[str, float], weights=None) -> float:
        if weights is None:
            weights = {"coherence": 0.35, "factuality": 0.35, "novelty": 0.15, "analogy": 0.1, "alignment": 0.05}
        s = 0.0
        for k, w in weights.items():
            s += scores.get(k, 0.0) * w
        return float(s)
