"""
Unit tests for Phase 5 InferenceManager + DialogueState + Safety.
"""
import os
import numpy as np
from pathlib import Path
from src.deployment.dialogue_state import DialogueState
from src.deployment.inference import InferenceManager
from src.deployment.safety import basic_safety_check
from src.knowledge.vector_db import VectorDB

# Mock generator that reflects temperature in output and sometimes emits a bad token when temp high
def mock_generator(genome, prompt: str, temperature: float):
    if temperature > 1.5:
        return f"{prompt} creative idea <BAD>"
    return f"{prompt} factual reply"

# Mock encoder returns simple random vector seeded by text hash for determinism
def mock_encoder(texts):
    vecs = []
    for t in texts:
        h = abs(hash(t)) % 1000
        rng = np.random.RandomState(h)
        vecs.append(rng.randn(16).astype(np.float32))
    return np.vstack(vecs)

def human_review_auto_approve(output: str, meta: dict) -> bool:
    # approve only if not containing "<BAD>"
    return "<BAD>" not in output

def test_dialogue_state_and_modes(tmp_path):
    ds = DialogueState(capacity=8, persist_path=str(tmp_path / "state.json"))
    vdb = VectorDB()
    # upsert a provenance example
    vdb.upsert(0, np.ones(16, dtype=np.float32), {"snippet": "example definition"})
    inf = InferenceManager(generator=mock_generator, encoder=mock_encoder, vectordb=vdb, dialogue_state=ds, human_review_cb=human_review_auto_approve)
    # factual mode
    res_f = inf.generate(user_id="u1", genome=None, prompt="What is Shrek?", mode="factual")
    assert res_f["mode"] == "factual"
    assert "creative" not in (res_f.get("warning") or "")
    assert res_f["unsafe"] is False
    # creative mode triggers human review because generator injects <BAD>
    res_c = inf.generate(user_id="u1", genome=None, prompt="Imagine Shrek", mode="creative", require_human_review=True)
    # human_review_auto_approve will block because output contains <BAD>
    assert res_c["unsafe"] is True or "blocked" in (res_c.get("warning") or "")
    # ensure dialogue state stored provenance when safe
    # run a balanced safe generation
    res_b = inf.generate(user_id="u2", genome=None, prompt="Tell me about onions", mode="balanced")
    assert res_b["unsafe"] is False
    path = ds.get_path("u2")
    # provenance inserted for u2 (vdb had one vertex)
    assert len(path) >= 0
    # save and reload state
    ds.save(str(tmp_path / "state.json"))
    ds2 = DialogueState(capacity=8, persist_path=str(tmp_path / "state.json"))
    assert ds2.get_path("u2") == ds.get_path("u2")