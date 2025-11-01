#!/usr/bin/env python3
"""
Test script to verify the generate_response function works correctly.
"""
import sys
import os

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

# Import the generate_response function from local_server.py
from local_server import generate_response

def test_generate_response():
    """Test the generate_response function with various prompts."""
    test_prompts = [
        "What is the capital of France?",
        "How many continents are there in the world?",
        "Explain quantum computing in simple terms",
        "Write a short poem about spring",
        "What is the tallest mountain in the world?"
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