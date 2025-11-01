#!/usr/bin/env python3
"""
Direct test of the GPT-2 generator function
"""

import sys
import os

# Add the project paths
project_root = os.path.dirname(os.path.abspath(__file__))
zoid_path = os.path.join(project_root, "gpt2_hypercube_phase1", "gpt2-hypercube-phase1")
sys.path.insert(0, zoid_path)
sys.path.insert(0, os.path.join(zoid_path, "src"))

def test_generator():
    """Test the GPT-2 generator function directly"""
    
    # Import the generator function
    try:
        # Add the scripts directory to the path
        sys.path.insert(0, os.path.join(project_root, "scripts"))
        
        # Import the generator function from the server
        import local_server
        generator_fn, encoder_fn = local_server.build_gpt2_generator()
        print("✓ Successfully created GPT-2 generator")
    except Exception as e:
        print(f"✗ Failed to create GPT-2 generator: {e}")
        return False
    
    # Test the generator
    try:
        # Create a mock genome (None for this test)
        genome = None
        prompt = "capital of Pakistan"
        
        # Generate a response
        response = generator_fn(genome, prompt)
        print(f"Generated response: {response}")
        
        # Check if response is a real AI response (not mock)
        mock_indicators = [
            "I'm not sure",
            "Question:",
            "History of America is a history of America"
        ]
        
        is_mock = any(indicator in response for indicator in mock_indicators)
        if is_mock:
            print(f"⚠️  Warning: Response appears to be mock/placeholder")
            return False
        else:
            print(f"✓ Response appears to be genuine AI output")
            return True
            
    except Exception as e:
        print(f"✗ Error generating response: {e}")
        return False

if __name__ == "__main__":
    print("Testing GPT-2 Generator Function")
    print("=" * 50)
    
    success = test_generator()
    
    if success:
        print("\n✅ Generator test completed successfully!")
        print("The GPT-2 generator is working correctly.")
    else:
        print("\n❌ Generator test failed!")
        print("There were issues with the GPT-2 generator.")
        
    sys.exit(0 if success else 1)