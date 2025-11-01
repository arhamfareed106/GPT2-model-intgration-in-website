"""
Root configuration file for pytest to ensure proper path setup.
"""
import sys
import os

# Add the src directory to the path so tests can import modules correctly
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')

# Insert at the beginning of the path to ensure our modules are found first
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
    
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Also add the project root to support absolute imports
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)