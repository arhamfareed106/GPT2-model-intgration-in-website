"""
Distiller that coordinates teacher->student distillation, curriculum, and safeguards.
Lightweight: teacher and student are callables/models with predictable interfaces.

Teacher API: teacher(inputs) -> dict with keys:
    - logits: Tensor (batch, seq_len, vocab)
    - concepts: Tensor (batch, concept_dim)
    - vertex_preds: LongTensor (batch, seq_len)  [optional]

Student API: student(inputs) -> similar dict, and student.parameters() for optimizer.

This module implements:
 - staged curriculum loop
 - combined loss (token KD + concept MSE + hypercube regularizer)
 - checkpointing & rollback when metrics drop beyond threshold
 - separate save for experimental vs production
"""
import os
import time
import torch
from typing import Callable, Optional, Dict, Any
from .curriculum import CurriculumSchedule
from .losses import token_lm_loss, concept_prediction_loss, hypercube_transition_regularizer

CHECKPOINT_DIR = "distill_checkpoints"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)


class Distiller:
    def __init__(
        self,
        teacher: Callable,
        student: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        curriculum: Optional[CurriculumSchedule] = None,
        evaluator: Optional[Callable[[str, str], Dict[str, float]]] = None,
        holdout_dataset=None,
        device: Optional[torch.device] = None,
        max_metric_drop: float = 0.10,
    ):
        self.teacher = teacher
        self.student = student
        self.optimizer = optimizer
        self.curriculum = curriculum or CurriculumSchedule()
        self.evaluator = evaluator
        self.holdout = holdout_dataset
        self.device = device or (torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu"))
        self.student.to(self.device)
        self.max_metric_drop = max_metric_drop
        self.best_prod_ckpt = None
        self.audit_log_path = os.path.join(CHECKPOINT_DIR, "audit.logl")

    def _save_checkpoint(self, name: str, experimental: bool = False):
        path = os.path.join(CHECKPOINT_DIR, f"{name}.pt")
        torch.save({"student_state": self.student.state_dict(), "meta": {"ts": int(time.time()), "experimental": experimental}}, path)
        # track production best
        if not experimental:
            self.best_prod_ckpt = path
        with open(self.audit_log_path, "a") as f:
            f.write(f"CKPT_SAVE {path} experimental={experimental} ts={int(time.time())}\n")
        return path

    def _rollback_to(self, path: str):
        if not os.path.exists(path):
            return False
        data = torch.load(path, map_location=self.device)
        self.student.load_state_dict(data["student_state"])
        with open(self.audit_log_path, "a") as f:
            f.write(f"CKPT_ROLLBACK {path} ts={int(time.time())}\n")
        return True

    def evaluate_holdout(self) -> Dict[str, float]:
        """
        Run evaluator over holdout if provided. Evaluator callable returns dict with metric names.
        For simplicity run single sample or aggregated.
        """
        if self.evaluator is None or self.holdout is None:
            return {}
        # simple aggregate over holdout items
        acc = {}
        n = 0
        for sample in self.holdout:
            prompt = sample.get("prompt", "")
            reference = sample.get("reference", "")
            # teacher/student generate texts via provided callables
            with torch.no_grad():
                student_out = self.student.generate(prompt) if hasattr(self.student, "generate") else ""
            metrics = self.evaluator(student_out, reference)
            for k, v in metrics.items():
                acc[k] = acc.get(k, 0.0) + v
            n += 1
            if n >= 20:
                break
        if n == 0:
            return {}
        for k in acc:
            acc[k] /= n
        return acc

    def run_distillation(self, dataloader, epochs: int = 1, experimental_stage: bool = False):
        """
        Main loop: iterate curriculum, perform distillation per batch.
        dataloader yields dicts with fields acceptable by teacher/student, e.g.:
            {"input_ids": Tensor, "labels": Tensor}
        """
        # Save pre-distill checkpoint for rollback safety
        pre_path = self._save_checkpoint("pre_distill", experimental=False)
        prod_metrics_before = self.evaluate_holdout() or {}
        for epoch in range(epochs):
            stage_name = self.curriculum.current_stage().name
            for batch in dataloader:
                self.student.train()
                # move tensors to device
                batch = {k: (v.to(self.device) if torch.is_tensor(v) else v) for k, v in batch.items()}
                # teacher forward
                with torch.no_grad():
                    tea_out = self.teacher(batch)
                stu_out = self.student(batch)
                # combined loss
                loss = torch.tensor(0.0, device=self.device)
                if "logits" in tea_out and "logits" in stu_out:
                    loss = loss + token_lm_loss(stu_out["logits"], tea_out["logits"], labels=batch.get("labels", None))
                if "concepts" in tea_out and "concepts" in stu_out:
                    loss = loss + concept_prediction_loss(stu_out["concepts"], tea_out["concepts"])
                if "vertex_preds" in stu_out and "vertex_preds" in tea_out:
                    penalty = hypercube_transition_regularizer(stu_out["vertex_preds"], allow_multi_bit=(stage_name=="constrained_pip_tasks"))
                    loss = loss + penalty * 0.1
                # step
                self.optimizer.zero_grad()
                loss.backward()
                # clip grads to avoid runaway drift
                torch.nn.utils.clip_grad_norm_(self.student.parameters(), max_norm=1.0)
                self.optimizer.step()
            # epoch finished
            self.curriculum.step_epoch()
            # checkpoint experimental vs production separation
            ckpt_name = f"epoch_{epoch}_{stage_name}_{'exp' if experimental_stage else 'prod'}"
            self._save_checkpoint(ckpt_name, experimental=experimental_stage)
            # evaluate holdout and enforce rollback if drop too large
            prod_metrics_after = self.evaluate_holdout() or {}
            if prod_metrics_before and prod_metrics_after:
                # compare a primary metric 'coherence' or fallback to first metric
                key = "coherence" if "coherence" in prod_metrics_before else list(prod_metrics_before.keys())[0]
                before = prod_metrics_before.get(key, 0.0)
                after = prod_metrics_after.get(key, 0.0)
                drop = (before - after) / max(1e-9, before) if before > 0 else 0.0
                if drop > self.max_metric_drop:
                    # rollback to pre-distill
                    self._rollback_to(pre_path)
                    return {"rolled_back": True, "reason": f"metric_drop_{drop:.3f}"}
            prod_metrics_before = prod_metrics_after
            # staged gating: only allow PIP stage if previous stages satisfied minimal metrics
            if stage_name == "long_form_chaining":
                # check baseline coherence/factuality thresholds before enabling PIP
                metrics = prod_metrics_after
                coh = metrics.get("coherence", 1.0)
                fact = metrics.get("factuality", 1.0)
                if coh < 0.6 or fact < 0.6:
                    # enforce rollback and abort PIP stage
                    self._rollback_to(pre_path)
                    return {"rolled_back": True, "reason": "pre_PIP_threshold_failed", "metrics": metrics}
            # continue until curriculum finished or epochs consumed
            if self.curriculum.is_finished():
                break
        return {"rolled_back": False}
