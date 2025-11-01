#!/usr/bin/env python3
"""
Test script to verify the short answer functionality.
"""
import requests
import json

def test_short_answers():
    """Test the server with questions that should return short, factual answers."""
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Health check: {response.json()}")
    except Exception as e:
        print(f"Error in health check: {e}")
    
    # Test questions that should return short, factual answers
    test_questions = [
        "What is the capital of Pakistan?",
        "What is the capital of USA?",
        "What is the capital of China?",
        "What is the capital of India?",
        "What is the capital of Japan?"
    ]
    
    print("\nTesting short, factual answers...")
    for question in test_questions:
        print(f"\nQuestion: {question}")
        try:
            payload = {
                "prompt": question,
                "user_id": "test_user"
            }
            response = requests.post(
                "http://localhost:5000/generate",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            result = response.json()
            print(f"Reply: {result.get('reply', 'No reply found')}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_short_answers()