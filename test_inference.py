#!/usr/bin/env python3
"""
Test script to verify the generate_response function works correctly.
"""
import sys
import os

# Add the Zoid project to the path
zoid_path = os.path.join(os.path.dirname(__file__), "gpt2_hypercube_phase1", "gpt2-hypercube-phase1")
sys.path.insert(0, zoid_path)
sys.path.insert(0, os.path.join(zoid_path, "src"))

print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")

# Try to import the generate_response function
try:
    # This should work with the path modifications above
    from deployment.inference import generate_response
    print("✅ Successfully imported generate_response")
except ImportError as e:
    print(f"❌ Failed to import generate_response: {e}")
    # Try direct import as fallback
    try:
        import importlib.util
        inference_file = os.path.join(zoid_path, "src", "deployment", "inference.py")
        if os.path.exists(inference_file):
            spec = importlib.util.spec_from_file_location("inference", inference_file)
            if spec is not None:
                inference_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(inference_module)
                generate_response = inference_module.generate_response
                print("✅ Successfully imported generate_response (direct)")
            else:
                print("❌ Failed to create module spec")
                sys.exit(1)
        else:
            print(f"❌ Inference file not found: {inference_file}")
            sys.exit(1)
    except Exception as e2:
        print(f"❌ Failed to import generate_response (direct): {e2}")
        sys.exit(1)

def test_generate_response():
    """Test the generate_response function with various prompts."""
    test_prompts = [
        "What is the capital of Italy?",
        "How many continents are there in the world?",
        "Explain quantum computing in simple terms"
    ]
    
    print("Testing generate_response function...")
    print("=" * 50)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}: {prompt}")
        print("-" * 30)
        
        try:
            response = generate_response(prompt)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    test_generate_response()