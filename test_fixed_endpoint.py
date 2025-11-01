#!/usr/bin/env python3
"""
Test script to verify the fixed endpoint implementation.
"""
import requests
import json

def test_fixed_endpoint():
    """Test the fixed /generate endpoint."""
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Health check: {response.json()}")
    except Exception as e:
        print(f"Error in health check: {e}")
    
    # Test the fixed endpoint with various inputs
    test_cases = [
        {"prompt": "capital of Pakistan", "user_id": "test1"},
        {"prompt": "What is the capital of USA?", "user_id": "test2"},
        {"prompt": "", "user_id": "test3"},  # Empty prompt
        {"invalid_key": "test"},  # Invalid format
    ]
    
    print("\nTesting fixed /generate endpoint...")
    for i, payload in enumerate(test_cases, 1):
        print(f"\nTest {i}: {payload}")
        try:
            response = requests.post(
                "http://localhost:5000/generate",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            result = response.json()
            print(f"Response: {result}")
            print(f"Status Code: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_fixed_endpoint()