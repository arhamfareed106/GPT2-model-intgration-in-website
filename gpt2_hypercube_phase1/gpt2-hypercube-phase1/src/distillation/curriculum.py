"""
Curriculum schedule for phased training.
Simple stage manager with names and epoch boundaries.
"""
from typing import List, Optional


class Stage:
    def __init__(self, name: str, epochs: int):
        self.name = name
        self.epochs = epochs
        self.completed = 0


class CurriculumSchedule:
    def __init__(self, stages: Optional[List[Stage]] = None):
        # Default 4-stage curriculum matching Phase 4 description
        if stages is None:
            stages = [
                Stage("definitions_paraphrase", 2),
                Stage("short_analogies_factual_qa", 2),
                Stage("long_form_chaining", 2),
                Stage("constrained_pip_tasks", 2),
            ]
        self.stages = stages
        self.current_idx = 0

    def current_stage(self) -> Stage:
        return self.stages[self.current_idx]

    def step_epoch(self) -> None:
        st = self.current_stage()
        st.completed += 1
        if st.completed >= st.epochs and self.current_idx < len(self.stages) - 1:
            self.current_idx += 1

    def is_finished(self) -> bool:
        return self.current_idx == len(self.stages) - 1 and self.current_stage().completed >= self.current_stage().epochs
