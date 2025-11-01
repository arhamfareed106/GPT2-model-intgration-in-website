#!/usr/bin/env python3
"""
Test script to verify the ChatAssistant implementation.
"""
import sys
import os
import json
import requests

# Add the Zoid project to the path
zoid_path = os.path.join(os.path.dirname(__file__), "gpt2_hypercube_phase1", "gpt2-hypercube-phase1")
sys.path.insert(0, zoid_path)
sys.path.insert(0, os.path.join(zoid_path, "src"))

def test_chat_assistant():
    """Test the ChatAssistant implementation."""
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Health check: {response.json()}")
    except Exception as e:
        print(f"Error in health check: {e}")
    
    # Test the original generate endpoint
    print("\nTesting original generate endpoint...")
    try:
        payload = {
            "prompt": "What is the capital of Italy?",
            "user_id": "test_user"
        }
        response = requests.post(
            "http://localhost:5000/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        result = response.json()
        print(f"Prompt: {payload['prompt']}")
        print(f"Response: {result['response']}")
    except Exception as e:
        print(f"Error in generate endpoint: {e}")
    
    # Test the new chat endpoint
    print("\nTesting new chat endpoint...")
    try:
        payload = {
            "prompt": "What is the capital of Italy?"
        }
        response = requests.post(
            "http://localhost:5000/chat",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        result = response.json()
        print(f"Prompt: {payload['prompt']}")
        print(f"Response: {result}")
    except Exception as e:
        print(f"Error in chat endpoint: {e}")

if __name__ == "__main__":
    test_chat_assistant()