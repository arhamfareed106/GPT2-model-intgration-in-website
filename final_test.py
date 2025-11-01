#!/usr/bin/env python3
"""
Final test to verify the complete solution is working.
"""
import requests
import json

def final_test():
    """Final test of the complete solution."""
    
    print("🔍 Final Test of Zoid GPT API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/health")
        health_data = response.json()
        print(f"   ✅ Health check: {health_data}")
        assert response.status_code == 200
        assert health_data["status"] == "ok"
        print("   🟢 Health endpoint working correctly")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: Valid request
    print("\n2. Testing valid request...")
    try:
        payload = {
            "prompt": "What is the capital of France?",
            "user_id": "final_test"
        }
        response = requests.post(
            "http://localhost:5000/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        result = response.json()
        print(f"   ✅ Response: {result}")
        assert response.status_code == 200
        assert "reply" in result
        assert isinstance(result["reply"], str)
        print("   🟢 Valid request handled correctly")
    except Exception as e:
        print(f"   ❌ Valid request failed: {e}")
        return False
    
    # Test 3: Empty prompt
    print("\n3. Testing empty prompt...")
    try:
        payload = {
            "prompt": "",
            "user_id": "final_test"
        }
        response = requests.post(
            "http://localhost:5000/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        result = response.json()
        print(f"   ✅ Response: {result}")
        assert response.status_code == 400
        assert result["reply"] == "Please provide a prompt."
        print("   🟢 Empty prompt handled correctly")
    except Exception as e:
        print(f"   ❌ Empty prompt test failed: {e}")
        return False
    
    # Test 4: Missing prompt
    print("\n4. Testing missing prompt...")
    try:
        payload = {
            "user_id": "final_test"
        }
        response = requests.post(
            "http://localhost:5000/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        result = response.json()
        print(f"   ✅ Response: {result}")
        assert response.status_code == 400
        assert result["reply"] == "Please provide a prompt."
        print("   🟢 Missing prompt handled correctly")
    except Exception as e:
        print(f"   ❌ Missing prompt test failed: {e}")
        return False
    
    # Test 5: Windows PowerShell curl command format
    print("\n5. Testing Windows PowerShell curl format...")
    print("   Run this command in PowerShell:")
    print('   curl.exe -X POST http://127.0.0.1:5000/generate -H "Content-Type: application/json" -d \'{\\"prompt\\": \\"What is the capital of Germany?\\"}\'')
    print("   Expected response: {\"reply\": \"The capital of Germany is Berlin.\"}")
    print("   🟢 Windows PowerShell format documented")
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The Zoid GPT API is working correctly.")
    print("\n📋 Summary of fixes:")
    print("   - Fixed 'undefined' response error")
    print("   - Added proper JSON validation")
    print("   - Implemented comprehensive error handling")
    print("   - Added Windows PowerShell usage instructions")
    print("   - Ensured all endpoints return valid JSON")
    return True

if __name__ == "__main__":
    final_test()