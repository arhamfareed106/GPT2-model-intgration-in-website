"""
Simple corpus ingestion utilities.
"""
import os
from typing import List


def ingest_text_files(paths: List[str]) -> List[str]:
    """
    Read plain text files and return list of documents (one per file).
    Missing files are skipped with a log.
    """
    docs = []
    for p in paths:
        if not os.path.exists(p):
            print(f"[ingest] missing: {p}")
            continue
        with open(p, "r", encoding="utf-8") as f:
            docs.append(f.read())
    return docs
