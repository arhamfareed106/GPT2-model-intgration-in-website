import requests
import json

# Test the health endpoint
try:
    health_response = requests.get("http://127.0.0.1:5000/health")
    print("Health endpoint response:")
    print(json.dumps(health_response.json(), indent=2))
    print()
except Exception as e:
    print(f"Error testing health endpoint: {e}")
    print()

# Test the generate endpoint
try:
    payload = {
        "user_id": "me",
        "prompt": "Tell me a funny story about AI.",
        "mode": "balanced",
        "max_new_tokens": 40
    }
    
    generate_response = requests.post(
        "http://127.0.0.1:5000/generate",
        json=payload
    )
    
    print("Generate endpoint response:")
    print(json.dumps(generate_response.json(), indent=2))
    print()
    
    if generate_response.status_code == 200:
        print("✅ Generate endpoint is working correctly")
        response_text = generate_response.json().get("response", "")
        print(f"Sample response: {response_text[:100]}...")
    else:
        print(f"❌ Generate endpoint failed with status code: {generate_response.status_code}")
        
except Exception as e:
    print(f"Error testing generate endpoint: {e}")
