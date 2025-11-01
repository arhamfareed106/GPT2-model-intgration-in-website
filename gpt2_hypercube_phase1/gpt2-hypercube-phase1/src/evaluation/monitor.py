"""
Memetic monitoring: track PIP-origin memes, acceptance rates, simple speciation/clustering, alarms.
"""
import os
import json
import time
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.cluster import KMeans

MONITOR_LOG = "phase6_monitor.log"


class MemeticMonitor:
    def __init__(self, audit_path: str = MONITOR_LOG):
        self.audit_path = audit_path
        self.memes = []  # list of dicts: {id, origin_pip, accepted, adapters (np.array), ts}
        os.makedirs(os.path.dirname(self.audit_path) or ".", exist_ok=True)

    def record_meme(self, meme_id: str, origin_pip: bool, accepted: bool, adapters: Optional[np.ndarray] = None):
        entry = {
            "id": meme_id,
            "origin_pip": bool(origin_pip),
            "accepted": bool(accepted),
            "adapters_shape": None if adapters is None else list(adapters.shape),
            "ts": int(time.time()),
        }
        # store adapters compactly if small
        if adapters is not None and adapters.size <= 256:
            entry["adapters"] = adapters.tolist()
        self.memes.append(entry)
        with open(self.audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def pip_acceptance_rate(self) -> float:
        pip = [m for m in self.memes if m["origin_pip"]]
        if not pip:
            return 0.0
        return float(sum(1 for m in pip if m["accepted"]) / max(1, len(pip)))

    def overall_acceptance_rate(self) -> float:
        if not self.memes:
            return 0.0
        return float(sum(1 for m in self.memes if m["accepted"]) / len(self.memes))

    def speciation(self, n_clusters: int = 3) -> Dict[int, int]:
        """
        Simple k-means on adapters (when available). Returns mapping meme_index -> cluster_id.
        Memes without adapters are ignored.
        """
        X = []
        idxs = []
        for i, m in enumerate(self.memes):
            if "adapters" in m and m["adapters"] is not None:
                X.append(m["adapters"])
                idxs.append(i)
        if not X:
            return {}
        X = np.array(X)
        k = min(n_clusters, len(X))
        km = KMeans(n_clusters=k, random_state=0).fit(X)
        mapping = {idxs[i]: int(int(km.labels_[i])) for i in range(len(idxs))}
        return mapping

    def alarm_if_drift(self, entropy: float, drift_thresh: float = 0.7) -> Optional[str]:
        if entropy >= drift_thresh:
            msg = f"ALARM: drift entropy {entropy:.3f} exceeds threshold {drift_thresh}"
            with open(self.audit_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"alarm": msg, "ts": int(time.time())}) + "\n")
            return msg
        return None
