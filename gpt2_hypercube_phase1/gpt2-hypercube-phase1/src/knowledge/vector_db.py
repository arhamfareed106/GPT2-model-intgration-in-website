"""
Lightweight in-memory vector DB keyed by vertex id with cosine NN retrieval.
"""
import os
import json
import pickle
from typing import Dict, List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class VectorDB:
    def __init__(self):
        # vertex_id -> vector (np.float32)
        self.vectors: Dict[int, np.ndarray] = {}
        # vertex_id -> canonical snippet / metadata
        self.meta: Dict[int, Dict] = {}

    def upsert(self, vertex_id: int, vector: np.ndarray, meta: Dict = None):
        self.vectors[int(vertex_id)] = np.asarray(vector, dtype=np.float32)
        self.meta[int(vertex_id)] = meta or {}

    def bulk_upsert(self, items: List[Tuple[int, np.ndarray, Dict]]):
        for vid, vec, m in items:
            self.upsert(vid, vec, m)

    def _stack(self):
        if not self.vectors:
            return np.zeros((0, 1), dtype=np.float32), []
        ids = sorted(self.vectors.keys())
        mat = np.vstack([self.vectors[i] for i in ids])
        return mat, ids

    def query(self, qvec: np.ndarray, top_k: int = 5):
        q = np.asarray(qvec, dtype=np.float32).reshape(1, -1)
        mat, ids = self._stack()
        if mat.shape[0] == 0:
            return []
        sims = cosine_similarity(q, mat)[0]
        idx = sims.argsort()[::-1][:top_k]
        results = []
        for i in idx:
            vid = ids[i]
            results.append({"vertex_id": int(vid), "score": float(sims[i]), "meta": self.meta.get(vid)})
        return results

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"vectors": self.vectors, "meta": self.meta}, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            d = pickle.load(f)
        self.vectors = d.get("vectors", {})
        self.meta = d.get("meta", {})
