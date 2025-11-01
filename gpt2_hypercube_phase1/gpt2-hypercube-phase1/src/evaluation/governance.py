"""
Governance utilities: audits, rollback registry, whitepaper/log generation, and review stubs.
"""
import os
import json
import time
from typing import List, Dict, Any, Optional

GOV_DIR = "phase6_governance"
os.makedirs(GOV_DIR, exist_ok=True)


class GovernanceManager:
    def __init__(self, gov_dir: str = GOV_DIR):
        self.gov_dir = gov_dir
        os.makedirs(self.gov_dir, exist_ok=True)
        self.audit_log = os.path.join(self.gov_dir, "audit.logl")
        self.rollback_paths: List[Dict[str, Any]] = []

    def schedule_quarterly_audit(self, description: str):
        entry = {"evt": "quarterly_audit", "desc": description, "ts": int(time.time())}
        with open(self.audit_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def register_rollback(self, ckpt_path: str, reason: str):
        entry = {"evt": "rollback_register", "ckpt": ckpt_path, "reason": reason, "ts": int(time.time())}
        self.rollback_paths.append(entry)
        with open(self.audit_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def publish_whitepaper(self, title: str, summary: str, filepath: Optional[str] = None):
        ts = int(time.time())
        doc = {"title": title, "summary": summary, "ts": ts}
        path = filepath or os.path.join(self.gov_dir, f"whitepaper_{ts}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2)
        with open(self.audit_log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"evt": "whitepaper_published", "path": path, "ts": ts}) + "\n")
        return path

    def human_review_lineage(self, memes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Placeholder: returns the memes annotated with 'human_ok' boolean.
        In real workflow, provide a UI for human committee to annotate.
        """
        reviewed = []
        for m in memes:
            m2 = m.copy()
            m2["human_ok"] = True  # optimistic default
            reviewed.append(m2)
        with open(self.audit_log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"evt": "lineage_review", "count": len(reviewed), "ts": int(time.time())}) + "\n")
        return reviewed
