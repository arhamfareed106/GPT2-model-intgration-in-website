"""
Bit-transition routing table for hypercube.

- BitTransitionTable builds adjacency lists (edges = Hamming distance 1).
- Save / load to/from JSON-friendly dict (vertex -> [neighbors]).
- Utility: edge_list() returns undirected edge tuples (u,v) with u < v.
"""
from typing import Dict, List, Tuple, Optional
import json
import os

from gpt2_hypercube_phase1.src.hypercube.topology import Hypercube


class BitTransitionTable:
    def __init__(self, hypercube: Hypercube):
        self.hypercube = hypercube
        # adjacency: int -> List[int]
        self.adjacency: Dict[int, List[int]] = {}
        self._build()

    def _build(self):
        self.adjacency = {}
        for v in self.hypercube.all_vertices():
            self.adjacency[int(v)] = self.hypercube.neighbors(int(v))

    def neighbors(self, vid: int) -> List[int]:
        return list(self.adjacency.get(int(vid), []))

    def edge_list(self) -> List[Tuple[int, int]]:
        """Return undirected edges as (u, v) with u < v."""
        edges = []
        for u, neighs in self.adjacency.items():
            for v in neighs:
                if u < v:
                    edges.append((u, v))
        return edges

    def save(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"n": self.hypercube.n, "adjacency": {str(k): v for k, v in self.adjacency.items()}}, f, indent=2)

    @classmethod
    def load(cls, path: str) -> "BitTransitionTable":
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        hc = Hypercube(int(d["n"]))
        table = cls(hc)
        # override adjacency if present
        adj_raw = d.get("adjacency", {})
        table.adjacency = {int(k): list(v) for k, v in adj_raw.items()}
        return table

    def shortest_route(self, a: int, b: int) -> Optional[List[int]]:
        """Proxy to hypercube.shortest_path for convenience."""
        return self.hypercube.shortest_path(a, b)
