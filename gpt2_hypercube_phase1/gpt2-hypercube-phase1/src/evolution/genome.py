"""
Genome and small utilities for EA population members.
"""
from dataclasses import dataclass, field
import numpy as np
import uuid
from typing import List, Dict, Any


@dataclass
class Genome:
    """
    Lightweight genome:
    - adapters: small adapter matrix (shape: adapter_dim)
    - concept_bias: vector bias for concept selection
    - hypercube_mask: bitmask preferences (list of 0/1 ints length n)
    - meta: lambda_con, mutation_rate, pip_mode flag
    """
    adapters: np.ndarray  # 1D array for simplicity
    concept_bias: np.ndarray
    hypercube_mask: List[int]
    meta: Dict[str, Any] = field(default_factory=lambda: {"lambda_con": 0.5, "mutation_rate": 0.1, "pip": False})
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def copy(self) -> "Genome":
        return Genome(
            adapters=self.adapters.copy(),
            concept_bias=self.concept_bias.copy(),
            hypercube_mask=list(self.hypercube_mask),
            meta=self.meta.copy(),
            id=self.id,
        )
