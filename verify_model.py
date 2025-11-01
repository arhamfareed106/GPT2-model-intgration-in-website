#!/usr/bin/env python3
"""
Verification script to check if the model is generating unique responses.
"""
import sys
import os

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

# Import the generate_response function from local_server.py
from local_server import generate_response

def verify_unique_responses():
    """Verify that the model generates unique responses for the same prompt."""
    prompt = "What is the capital of France?"
    
    print("Verifying unique responses for the same prompt...")
    print("=" * 50)
    
    responses = []
    for i in range(5):
        print(f"\nGeneration {i+1}:")
        print("-" * 20)
        
        try:
            response = generate_response(prompt)
            responses.append(response)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Check for uniqueness
    unique_responses = set(responses)
    print(f"\nResults:")
    print(f"Total responses: {len(responses)}")
    print(f"Unique responses: {len(unique_responses)}")
    
    if len(unique_responses) == len(responses):
        print("✅ All responses are unique!")
    else:
        print("⚠️  Some responses are duplicates.")
    
    print("\n" + "=" * 50)
    
    # Test with different prompts
    print("\nTesting with different prompts...")
    print("-" * 30)
    
    prompts = [
        "What is the capital of France?",
        "What is the capital of Germany?",
        "What is the capital of Japan?"
    ]
    
    prompt_responses = {}
    for prompt in prompts:
        response = generate_response(prompt)
        prompt_responses[prompt] = response
        print(f"\nPrompt: {prompt}")
        print(f"Response: {response}")
    
    # Check if responses for different prompts are different
    response_values = list(prompt_responses.values())
    unique_response_values = set(response_values)
    
    print(f"\nResults:")
    print(f"Total prompts: {len(prompts)}")
    print(f"Unique responses: {len(unique_response_values)}")
    
    if len(unique_response_values) == len(prompts):
        print("✅ All responses for different prompts are unique!")
    else:
        print("⚠️  Some responses for different prompts are the same.")

if __name__ == "__main__":
    verify_unique_responses()