"""
Concept grounding onto hypercube vertices.

- Default encoder: sklearn TfidfVectorizer + TruncatedSVD (lightweight).
- Mapping rules:
  * synonyms -> adjacent vertices
  * antonyms -> complement vertex
  * hierarchies -> simple path assignment (flip one bit per level)
- Confidence threshold enforced (default 0.75).
- Versioned mapping saved as JSON with timestamp.
"""
import os
import json
import time
from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from ..hypercube.topology import Hypercube


class SimpleEncoder:
    """Lightweight TF-IDF + SVD encoder for embeddings."""
    def __init__(self, dim: int = 64):
        self.dim = dim
        self._vec = TfidfVectorizer(max_features=5000)
        self._svd = TruncatedSVD(n_components=min(dim, 32))
        self._fitted = False

    def fit(self, texts: List[str]):
        X = self._vec.fit_transform(texts)
        Xs = self._svd.fit_transform(X)
        Xs = normalize(Xs)
        self._fitted = True
        return Xs

    def encode(self, texts: List[str]) -> np.ndarray:
        if not self._fitted:
            # fit on the same texts (cheap fallback)
            self.fit(texts)
        X = self._vec.transform(texts)
        Xs = self._svd.transform(X)
        return normalize(Xs)


class ConceptGrounder:
    def __init__(
        self,
        hypercube: Hypercube,
        encoder: Optional[SimpleEncoder] = None,
        prototype_init: Optional[np.ndarray] = None,
        conf_threshold: float = 0.75,
        mapping_dir: str = "mappings",
    ):
        self.hypercube = hypercube
        self.encoder = encoder or SimpleEncoder(dim=64)
        # prototype vectors per vertex_id; if provided used, else random
        if prototype_init is not None:
            assert prototype_init.shape[0] == hypercube.vertex_count
            self.prototypes = np.asarray(prototype_init, dtype=np.float32)
        else:
            rng = np.random.RandomState(42)
            self.prototypes = rng.randn(hypercube.vertex_count, 32).astype(np.float32)
            # normalize
            self.prototypes = self.prototypes / (np.linalg.norm(self.prototypes, axis=1, keepdims=True) + 1e-9)
        self.conf_threshold = conf_threshold
        self.mapping_dir = mapping_dir
        os.makedirs(self.mapping_dir, exist_ok=True)
        # mappings:
        self.concept_to_vertex: Dict[str, Optional[int]] = {}
        self.version_history: List[Dict] = []

    def _nearest_vertex(self, vec: np.ndarray) -> Tuple[int, float]:
        sims = cosine_similarity(vec.reshape(1, -1), self.prototypes)[0]
        idx = int(sims.argmax())
        return idx, float(sims[idx])

    def encode(self, texts: List[str]) -> np.ndarray:
        return self.encoder.encode(texts)

    def assign_single(self, concept: str, vector: np.ndarray) -> Optional[int]:
        vid, score = self._nearest_vertex(vector)
        if score < self.conf_threshold:
            return None
        return int(vid)

    def assign_bulk(self, concepts: List[str], texts_for_encoder: Optional[List[str]] = None):
        # Fit encoder if not already
        if texts_for_encoder is None:
            texts_for_encoder = concepts
        self.encoder.fit(texts_for_encoder)
        vecs = self.encode(concepts)
        for i, c in enumerate(concepts):
            assigned = self.assign_single(c, vecs[i])
            self.concept_to_vertex[c] = assigned

    def enforce_synonyms(self, groups: List[List[str]]):
        """
        For each synonym group, pick an anchor (first assigned or nearest) and
        assign other members to neighbors (Hamming distance 1) if confidence allows.
        """
        for group in groups:
            # encode group
            vecs = self.encode(group)
            # find anchor: first with existing assignment else nearest to its own prototype
            anchor_vid = None
            for i, c in enumerate(group):
                if c in self.concept_to_vertex and self.concept_to_vertex[c] is not None:
                    anchor_vid = self.concept_to_vertex[c]
                    break
            if anchor_vid is None:
                # pick first's nearest
                anchor_vid, score = self._nearest_vertex(vecs[0])
                if score < self.conf_threshold:
                    # fallback: skip group
                    continue
                self.concept_to_vertex[group[0]] = int(anchor_vid)
            # now assign neighbors to other terms
            neighs = self.hypercube.neighbors(anchor_vid)
            j = 0
            for i, c in enumerate(group):
                if c in self.concept_to_vertex and self.concept_to_vertex[c] is not None:
                    continue
                if j >= len(neighs):
                    break
                vid_candidate = neighs[j]
                # check similarity to candidate prototype
                score = cosine_similarity(vecs[i].reshape(1, -1), self.prototypes[vid_candidate].reshape(1, -1))[0, 0]
                if score >= self.conf_threshold:
                    self.concept_to_vertex[c] = int(vid_candidate)
                    j += 1

    def enforce_antonyms(self, pairs: List[Tuple[str, str]]):
        """
        For each antonym pair, assign one to vid and the other to complement(vid).
        """
        for a, b in pairs:
            # ensure both encoded
            vecs = self.encode([a, b])
            a_vid, a_score = self._nearest_vertex(vecs[0])
            if a_score < self.conf_threshold:
                continue
            b_vid, b_score = self._nearest_vertex(vecs[1])
            # prefer to place b at complement of a
            comp = self.hypercube.complement(a_vid)
            comp_score = cosine_similarity(vecs[1].reshape(1, -1), self.prototypes[comp].reshape(1, -1))[0, 0]
            if comp_score >= self.conf_threshold:
                self.concept_to_vertex[a] = int(a_vid)
                self.concept_to_vertex[b] = int(comp)
            else:
                # fallback to nearest if above threshold
                if b_score >= self.conf_threshold:
                    self.concept_to_vertex[a] = int(a_vid)
                    self.concept_to_vertex[b] = int(b_vid)

    def enforce_hierarchy(self, paths: List[List[str]]):
        """
        Each path is a list [hypernym, ... , hyponym].
        Map to a simple path on the hypercube: start at nearest vertex then flip one bit per step.
        """
        for path in paths:
            vecs = self.encode(path)
            start_vid, start_score = self._nearest_vertex(vecs[0])
            if start_score < self.conf_threshold:
                continue
            current = start_vid
            self.concept_to_vertex[path[0]] = int(current)
            for i in range(1, len(path)):
                # pick a neighbor that improves similarity if possible
                candidates = [current] + self.hypercube.neighbors(current)
                best_vid = current
                best_score = -1.0
                for cand in candidates:
                    s = cosine_similarity(vecs[i].reshape(1, -1), self.prototypes[cand].reshape(1, -1))[0, 0]
                    if s > best_score:
                        best_vid = cand
                        best_score = s
                if best_score >= self.conf_threshold:
                    current = best_vid
                    self.concept_to_vertex[path[i]] = int(current)
                else:
                    # leave unassigned if confidence low
                    self.concept_to_vertex[path[i]] = None

    def save_mapping(self, name: Optional[str] = None) -> str:
        ts = int(time.time())
        name = name or f"mapping_{ts}.json"
        path = os.path.join(self.mapping_dir, name)
        data = {
            "timestamp": ts,
            "n": self.hypercube.n,
            "mapping": {k: v if v is None else int(v) for k, v in self.concept_to_vertex.items()},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        # add to history
        self.version_history.append({"path": path, "timestamp": ts})
        return path

    def load_mapping(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.concept_to_vertex = {k: (None if v is None else int(v)) for k, v in data["mapping"].items()}
        self.version_history.append({"path": path, "timestamp": data.get("timestamp", int(time.time()))})
