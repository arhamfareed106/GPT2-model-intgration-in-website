"""
Per-user dialogue state holding last-N hypercube vertices (and short token context).
Provides persistence and simple utilities.
"""
from collections import defaultdict, deque
import json
import os
from typing import List, Optional

DEFAULT_CAP = 16


class DialogueState:
    def __init__(self, capacity: int = DEFAULT_CAP, persist_path: Optional[str] = None):
        self.capacity = capacity
        self.states = defaultdict(lambda: deque(maxlen=self.capacity))  # user_id -> deque of vertex ids
        self.token_context = defaultdict(lambda: deque(maxlen=self.capacity))  # user_id -> recent short tokens
        self.persist_path = persist_path
        if persist_path and os.path.exists(persist_path):
            try:
                with open(persist_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for uid, seq in data.get("states", {}).items():
                    self.states[uid] = deque(seq, maxlen=self.capacity)
                for uid, seq in data.get("tokens", {}).items():
                    self.token_context[uid] = deque(seq, maxlen=self.capacity)
            except Exception:
                pass

    def push_vertex(self, user_id: str, vertex_id: int):
        self.states[user_id].append(int(vertex_id))

    def get_path(self, user_id: str, last_k: Optional[int] = None) -> List[int]:
        seq = list(self.states[user_id])
        if last_k:
            return seq[-last_k:]
        return seq

    def push_tokens(self, user_id: str, tokens: List[str]):
        for t in tokens:
            self.token_context[user_id].append(t)

    def get_tokens(self, user_id: str, last_k: Optional[int] = None) -> List[str]:
        seq = list(self.token_context[user_id])
        if last_k:
            return seq[-last_k:]
        return seq

    def save(self, path: Optional[str] = None):
        path = path or self.persist_path
        if not path:
            raise ValueError("No persist path provided")
        data = {
            "states": {uid: list(d) for uid, d in self.states.items()},
            "tokens": {uid: list(d) for uid, d in self.token_context.items()},
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def clear_user(self, user_id: str):
        self.states[user_id].clear()
        self.token_context[user_id].clear()
