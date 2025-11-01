import requests
import json

# Test the health endpoint
response = requests.get("http://127.0.0.1:5000/health")
print("Health check:", response.json())

# Test the generate endpoint
data = {
    "prompt": "Hello, how are you?",
    "user_id": "test_user"
}

response = requests.post(
    "http://127.0.0.1:5000/generate",
    headers={"Content-Type": "application/json"},
    data=json.dumps(data)
)

print("Generate response:", response.json())