#!/usr/bin/env python3
"""
Simple test script to verify that the backend server is working correctly
"""

import requests
import json

def test_backend():
    # Test health endpoint
    try:
        health_response = requests.get("http://127.0.0.1:5000/health")
        print("Health check:", health_response.json())
    except Exception as e:
        print("Health check failed:", str(e))
        return False
    
    # Test generate endpoint
    try:
        generate_response = requests.post(
            "http://127.0.0.1:5000/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "prompt": "Hello, how are you?",
                "user_id": "test_user"
            })
        )
        print("Generate response:", generate_response.json())
        return True
    except Exception as e:
        print("Generate test failed:", str(e))
        return False

if __name__ == "__main__":
    print("Testing Zoid GPT backend...")
    if test_backend():
        print("✅ All tests passed! Backend is working correctly.")
    else:
        print("❌ Tests failed. Please check the backend server.")