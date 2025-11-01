# shim package to expose the real src tree located in the hyphenated folder
import os

# real source location (workspace root / gpt2-hypercube-phase1/src)
_real_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "gpt2-hypercube-phase1", "src"))

if os.path.isdir(_real_src) and _real_src not in __path__:
    __path__.append(_real_src)
