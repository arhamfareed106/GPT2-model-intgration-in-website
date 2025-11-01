"""
Root configuration file for pytest to ensure proper path setup for the entire project.
"""
import sys
import os

# Add the nested src directory to the path so tests can import modules correctly
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
NESTED_SRC = os.path.join(PROJECT_ROOT, 'gpt2_hypercube_phase1', 'gpt2-hypercube-phase1', 'src')

# Insert at the beginning of the path to ensure our modules are found first
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if NESTED_SRC not in sys.path:
    sys.path.insert(0, NESTED_SRC)