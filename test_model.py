#!/usr/bin/env python3
"""
Simple test script to verify the Zoid GPT model responses
"""

import requests
import json

def test_model():
    # Test health endpoint
    try:
        health_response = requests.get("http://127.0.0.1:5000/health")
        print("Health check:", health_response.json())
    except Exception as e:
        print("Health check failed:", str(e))
        return False
    
    # Test generate endpoint
    test_prompts = [
        "capital of Pakistan",
        "world largest country in area", 
        "capital of Italy",
        "history of America in 12 words"
    ]
    
    print("\nTesting model responses:")
    print("-" * 50)
    
    for prompt in test_prompts:
        try:
            response = requests.post(
                "http://127.0.0.1:5000/generate",
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "prompt": prompt,
                    "user_id": "test_user"
                })
            )
            
            result = response.json()
            print(f"Prompt: {prompt}")
            print(f"Response: {result.get('reply', 'No reply field')}")
            print("-" * 50)
            
        except Exception as e:
            print(f"Error testing '{prompt}': {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Testing Zoid GPT Model Responses")
    print("=" * 50)
    
    success = test_model()
    
    if success:
        print("\n✅ All tests completed!")
    else:
        print("\n❌ Tests failed!")