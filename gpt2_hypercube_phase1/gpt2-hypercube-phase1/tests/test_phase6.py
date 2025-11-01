"""
Unit tests for Phase 6 evaluation & governance scaffolds.
"""
import numpy as np
from pathlib import Path
import os
import pytest
from src.evaluation.metrics import (
    coherence_score, factuality_score, novelty_score, hypercube_path_entropy, memory_fidelity
)
from src.evaluation.monitor import MemeticMonitor
from src.evaluation.governance import GovernanceManager
from src.knowledge.vector_db import VectorDB

def test_metrics_and_monitor(tmp_path):
    # coherence
    assert coherence_score([0.8, 0.7, 0.9]) == pytest.approx(0.8, rel=1e-3)
    # vectordb usage
    vdb = VectorDB()
    vec = np.ones(16, dtype=np.float32)
    vdb.upsert(0, vec, {"snippet": "a"})
    # factuality: query vector close to stored -> high factuality
    qvec = np.ones(16, dtype=np.float32)
    f = factuality_score("o", qvec, vdb, top_k=1, sim_thresh=0.5)
    assert f >= 0.0 and f <= 1.0
    # novelty: when identical vector present -> low novelty
    n = novelty_score(qvec, vdb)
    assert 0.0 <= n <= 1.0
    # hypercube entropy
    paths = [[0,1,0],[0,1,2]]
    e = hypercube_path_entropy(paths)
    assert 0.0 <= e <= 1.0
    # memory fidelity
    mf = memory_fidelity([[1,2,3]], [[1,3]])
    assert mf == pytest.approx(2/3, rel=1e-3)

    # memetic monitor
    mm = MemeticMonitor(str(tmp_path / "monitor.log"))
    mm.record_meme("m1", origin_pip=True, accepted=True, adapters=np.zeros(8))
    mm.record_meme("m2", origin_pip=False, accepted=False, adapters=np.ones(8))
    assert mm.pip_acceptance_rate() == pytest.approx(1.0)
    assert 0.5 <= mm.overall_acceptance_rate() <= 1.0
    spec = mm.speciation(n_clusters=2)
    assert isinstance(spec, dict)

def test_governance(tmp_path):
    gm = GovernanceManager(gov_dir=str(tmp_path))
    a = gm.schedule_quarterly_audit("Q1 review")
    assert "evt" in a
    wp = gm.publish_whitepaper("T", "S", filepath=str(tmp_path / "wp.json"))
    assert Path(wp).exists()
    gm.register_rollback("ckpt.pt", "safety")
    reviewed = gm.human_review_lineage([{"id":"m1"}])
    assert reviewed[0]["human_ok"] is True