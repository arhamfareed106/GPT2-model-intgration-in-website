#!/usr/bin/env python3
"""
Script to verify the project setup and identify issues.
"""
import sys
import os

print("Python version:", sys.version)
print("Python path:", sys.path)

# Check current working directory
print("Current working directory:", os.getcwd())

# Try to import required modules
modules_to_test = [
    "flask",
    "flask_cors",
    "numpy",
    "torch",
    "transformers"
]

print("\nTesting module imports:")
for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ {module}: OK")
    except ImportError as e:
        print(f"❌ {module}: {e}")

# Check Zoid project structure
print("\nChecking Zoid project structure:")
zoid_path = os.path.join(os.getcwd(), "gpt2_hypercube_phase1", "gpt2-hypercube-phase1")
print(f"Zoid path: {zoid_path}")
print(f"Zoid path exists: {os.path.exists(zoid_path)}")

if os.path.exists(zoid_path):
    src_path = os.path.join(zoid_path, "src")
    print(f"Src path: {src_path}")
    print(f"Src path exists: {os.path.exists(src_path)}")
    
    if os.path.exists(src_path):
        deployment_path = os.path.join(src_path, "deployment")
        print(f"Deployment path: {deployment_path}")
        print(f"Deployment path exists: {os.path.exists(deployment_path)}")
        
        if os.path.exists(deployment_path):
            files = os.listdir(deployment_path)
            print(f"Files in deployment: {files}")

# Test sys.path modifications
print("\nTesting sys.path modifications:")
zoid_src_path = os.path.join(zoid_path, "src")
sys.path.insert(0, zoid_path)
sys.path.insert(0, zoid_src_path)

print(f"Added to sys.path: {zoid_path}")
print(f"Added to sys.path: {zoid_src_path}")

# Try to import Zoid components
print("\nTesting Zoid component imports:")
try:
    from deployment.inference import InferenceManager
    print("✅ InferenceManager: OK")
except ImportError as e:
    print(f"❌ InferenceManager: {e}")

try:
    from deployment.inference import generate_response
    print("✅ generate_response: OK")
except ImportError as e:
    print(f"❌ generate_response: {e}")