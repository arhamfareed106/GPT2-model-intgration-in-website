#!/usr/bin/env python3
"""
Test script to verify the system is working correctly for preview.
"""
import requests
import json

def test_system():
    """Test the system for preview."""
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Health check: {response.json()}")
    except Exception as e:
        print(f"Error in health check: {e}")
    
    # Test generate endpoint with a simple question
    print("\nTesting generate endpoint...")
    try:
        payload = {
            "prompt": "What is the capital of France?",
            "user_id": "preview_user"
        }
        response = requests.post(
            "http://localhost:5000/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        result = response.json()
        print(f"Question: {payload['prompt']}")
        print(f"Reply: {result.get('reply', 'No reply found')}")
    except Exception as e:
        print(f"Error in generate endpoint: {e}")

if __name__ == "__main__":
    test_system()