"""
Hypercube topology utilities.
"""
import itertools
from typing import List


class Hypercube:
    def __init__(self, n: int):
        assert n >= 1 and isinstance(n, int)
        self.n = n
        self.vertex_count = 1 << n

    def vertex_id(self, bits: List[int]) -> int:
        """Convert list of 0/1 bits (length n) to integer vertex id."""
        assert len(bits) == self.n
        vid = 0
        for b in bits:
            vid = (vid << 1) | (1 if b else 0)
        return vid

    def bits_of(self, vid: int) -> List[int]:
        assert 0 <= vid < self.vertex_count
        return [(vid >> (self.n - 1 - i)) & 1 for i in range(self.n)]

    def hamming(self, a: int, b: int) -> int:
        return bin(a ^ b).count("1")

    def neighbors(self, vid: int) -> List[int]:
        """Return all vertices at Hamming distance 1 (neighbors)."""
        neigh = []
        for i in range(self.n):
            neigh.append(vid ^ (1 << i))
        return neigh

    def complement(self, vid: int) -> int:
        mask = (1 << self.n) - 1
        return vid ^ mask

    def all_vertices(self) -> List[int]:
        return list(range(self.vertex_count))
