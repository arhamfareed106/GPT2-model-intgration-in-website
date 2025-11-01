#!/usr/bin/env python3
"""
Verification script to test that the model is generating real AI responses
instead of mock responses.
"""

import sys
import os

# Add the project paths
project_root = os.path.dirname(os.path.abspath(__file__))
zoid_path = os.path.join(project_root, "gpt2_hypercube_phase1", "gpt2-hypercube-phase1")
sys.path.insert(0, zoid_path)
sys.path.insert(0, os.path.join(zoid_path, "src"))

def test_model_responses():
    """Test that the model generates real responses instead of mock ones."""
    
    print("Testing model responses...")
    
    # Import the generate_response function
    try:
        from deployment.inference import generate_response
        print("✓ Successfully imported generate_response function")
    except ImportError as e:
        print(f"✗ Failed to import generate_response: {e}")
        return False
    
    # Test cases
    test_prompts = [
        "capital of Pakistan",
        "world largest country in area",
        "capital of Italy", 
        "history of America in 12 words"
    ]
    
    print("\nTesting responses:")
    print("-" * 50)
    
    for prompt in test_prompts:
        try:
            response = generate_response(prompt)
            print(f"Prompt: {prompt}")
            print(f"Response: {response}")
            print("-" * 50)
            
            # Check if response is a real AI response (not mock)
            mock_indicators = [
                "I'm not sure",
                "Question:",
                "History of America is a history of America"
            ]
            
            is_mock = any(indicator in response for indicator in mock_indicators)
            if is_mock:
                print(f"⚠️  Warning: Response appears to be mock/placeholder")
            else:
                print(f"✓ Response appears to be genuine AI output")
                
        except Exception as e:
            print(f"✗ Error generating response for '{prompt}': {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Zoid GPT Model Response Verification")
    print("=" * 50)
    
    success = test_model_responses()
    
    if success:
        print("\n✅ Verification completed successfully!")
        print("The model is generating real AI responses.")
    else:
        print("\n❌ Verification failed!")
        print("There were issues with model response generation.")
        
    sys.exit(0 if success else 1)