"""
Unit test for Phase 4 distillation scaffold.
Uses tiny mock teacher/student to verify loop, checkpointing and rollback guard.
"""
import os
import torch
import tempfile
from pathlib import Path
from src.distillation.distiller import Distiller, CHECKPOINT_DIR
from src.distillation.curriculum import CurriculumSchedule
from torch import nn
from torch.utils.data import DataLoader


# Minimal mock teacher / student
class MockModel(nn.Module):
    def __init__(self, vocab_size=32, concept_dim=8):
        super().__init__()
        self.embed = nn.Embedding(64, 16)
        self.head = nn.Linear(16, vocab_size)
        self.concept_head = nn.Linear(16, concept_dim)

    def forward(self, batch):
        # expects input_ids: (batch, seq_len)
        ids = batch["input_ids"]
        x = self.embed(ids).mean(dim=1)
        logits = self.head(x).unsqueeze(1).repeat(1, ids.size(1), 1)
        concepts = self.concept_head(x)
        # vertex_preds is dummy zeros
        vertex_preds = torch.zeros(ids.size(0), ids.size(1), dtype=torch.long)
        return {"logits": logits, "concepts": concepts, "vertex_preds": vertex_preds}

    # convenience for distiller evaluate_holdout
    def generate(self, prompt: str):
        return f"mock_out {prompt}"


def simple_dataloader(batch_size=4, batches=3, seq_len=6, vocab_size=32):
    data = []
    for _ in range(batches):
        input_ids = torch.randint(0, 64, (batch_size, seq_len))
        labels = torch.randint(0, vocab_size, (batch_size, seq_len))
        data.append({"input_ids": input_ids, "labels": labels})
    return DataLoader(data, batch_size=None)


def simple_evaluator(output: str, reference: str):
    # trivial evaluator that gives 0.8 coherence and 0.8 factuality for any non-empty output
    return {"coherence": 0.8, "factuality": 0.8}


def test_distillation_run(tmp_path):
    # ensure checkpoint dir is inside tmp to avoid polluting workspace
    os.environ["DISTILL_CHECKPOINT_DIR"] = str(tmp_path)
    teacher = MockModel()
    student = MockModel()
    opt = torch.optim.Adam(student.parameters(), lr=1e-3)
    curriculum = CurriculumSchedule()
    holdout = [{"prompt": "q1", "reference": "a1"}]
    dist = Distiller(teacher=teacher, student=student, optimizer=opt, curriculum=curriculum, evaluator=simple_evaluator, holdout_dataset=holdout, device=torch.device("cpu"), max_metric_drop=0.5)
    dl = simple_dataloader()
    res = dist.run_distillation(dl, epochs=1, experimental_stage=False)
    assert isinstance(res, dict)
    # check checkpoint dir exists and at least one checkpoint file present
    assert os.path.isdir("distill_checkpoints")
    files = list(Path("distill_checkpoints").glob("*.pt"))
    assert len(files) >= 1