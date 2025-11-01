# top-level 'src' package shim that points to the actual source under gpt2-hypercube-phase1/src
import os

_real_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "gpt2-hypercube-phase1", "src"))
if os.path.isdir(_real_src) and _real_src not in __path__:
    __path__.append(_real_src)
