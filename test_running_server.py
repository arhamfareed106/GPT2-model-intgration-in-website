#!/usr/bin/env python3
"""
Test script to verify the running server is working correctly.
"""
import requests
import json

def test_server():
    """Test the running server endpoints."""
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Health check: {response.json()}")
    except Exception as e:
        print(f"Error in health check: {e}")
    
    # Test generate endpoint
    print("\nTesting generate endpoint...")
    try:
        payload = {
            "prompt": "Hello, how are you?",
            "user_id": "test_user"
        }
        response = requests.post(
            "http://localhost:5000/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print(f"Generate response: {response.json()}")
    except Exception as e:
        print(f"Error in generate endpoint: {e}")

if __name__ == "__main__":
    test_server()