"""
Simple retrieval API that returns top-k vertex candidates with snippets.
"""
from typing import List, Dict
import numpy as np


class RetrievalAPI:
    def __init__(self, encoder, vectordb):
        """
        encoder: callable that takes list[str] -> np.ndarray embeddings
        vectordb: VectorDB instance
        """
        self.encoder = encoder
        self.vectordb = vectordb

    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        qvec = self.encoder([query])[0]
        return self.vectordb.query(qvec, top_k=k)
