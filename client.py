#!/usr/bin/env python3
"""
Simple client script to interact with the Zoid GPT API
"""

import requests
import json
import sys

def send_prompt(prompt, user_id="user", mode="balanced", max_new_tokens=100):
    """
    Send a prompt to the Zoid GPT API and return the response
    """
    url = "http://127.0.0.1:5000/generate"
    payload = {
        "user_id": user_id,
        "prompt": prompt,
        "mode": mode,
        "max_new_tokens": max_new_tokens
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return None

def check_health():
    """
    Check if the server is running
    """
    try:
        response = requests.get("http://127.0.0.1:5000/health")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return None

def main():
    print("Zoid GPT Client")
    print("=" * 50)
    
    # Check if server is running
    health = check_health()
    if health:
        print(f"✅ Server is running (model: {health['model']})")
    else:
        print("❌ Server is not accessible. Please start the server first.")
        print("   Run: python scripts/local_server.py --host 127.0.0.1 --port 5000")
        return
    
    print("\nUsage: Enter your prompt or 'quit' to exit")
    print("       Use 'health' to check server status")
    print("-" * 50)
    
    while True:
        try:
            prompt = input("\n> ").strip()
            
            if prompt.lower() == 'quit':
                print("Goodbye!")
                break
            elif prompt.lower() == 'health':
                health = check_health()
                if health:
                    print(f"Server status: OK (model: {health['model']})")
                else:
                    print("Server is not accessible")
                continue
            elif not prompt:
                continue
                
            print("Generating response...")
            result = send_prompt(prompt)
            
            if result:
                print(f"\nResponse: {result['response']}")
                if result.get('provenance'):
                    print(f"Provenance: {len(result['provenance'])} items")
            else:
                print("Failed to get response from server")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break

if __name__ == "__main__":
    main()
