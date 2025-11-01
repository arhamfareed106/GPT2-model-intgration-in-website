"""
Lightweight inference-time safety checks and fallback policy.
Replace or extend with real detectors (toxicity, hallucination, factuality).
"""
from typing import Tuple, Callable, Optional


BAD_TOKEN_BLACKLIST = {"<BAD>", "<unsafe>", "kill", "bomb"}


def basic_safety_check(output: str) -> Tuple[bool, str]:
    """
    Returns (is_safe, reason). Simple heuristics:
    - presence of blacklist tokens -> unsafe
    - excessive token repetition -> unsafe
    """
    if not output:
        return False, "empty_output"
    lowered = output.lower()
    for bad in BAD_TOKEN_BLACKLIST:
        if bad.lower() in lowered:
            return False, f"blacklist_token:{bad}"
    toks = output.split()
    if len(toks) > 0:
        uniq = len(set(toks))
        if uniq / max(1, len(toks)) < 0.05:
            return False, "repetition"
    return True, "ok"


def fallback_safe_response(prompt: str) -> str:
    return "I'm not able to help with that right now. Please try rephrasing or request human assistance."
