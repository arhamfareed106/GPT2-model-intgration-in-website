#!/usr/bin/env python3
"""
Test script for Windows users to verify the Flask endpoint.
"""
import requests
import json

def test_endpoint():
    """Test the /generate endpoint with proper JSON."""
    
    # Test health endpoint first
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Health check: {response.json()}")
    except Exception as e:
        print(f"Error in health check: {e}")
        return
    
    # Test the generate endpoint with proper JSON
    print("\nTesting /generate endpoint...")
    
    # Test case 1: Valid request
    print("\n1. Testing with valid prompt...")
    try:
        payload = {
            "prompt": "capital of Pakistan",
            "user_id": "windows_test"
        }
        response = requests.post(
            "http://localhost:5000/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test case 2: Empty prompt
    print("\n2. Testing with empty prompt...")
    try:
        payload = {
            "prompt": "",
            "user_id": "windows_test"
        }
        response = requests.post(
            "http://localhost:5000/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test case 3: Missing prompt
    print("\n3. Testing with missing prompt...")
    try:
        payload = {
            "user_id": "windows_test"
        }
        response = requests.post(
            "http://localhost:5000/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoint()