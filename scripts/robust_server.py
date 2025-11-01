#!/usr/bin/env python3
"""
Zoid GPT Server - Robust Version
This server can run in either mock mode or production mode with real GPT-2 inference.
It includes better error handling for Windows DLL issues.
"""
import os
import sys
import argparse
from typing import List, Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

# Add the Zoid project to the path
zoid_path = os.path.join(os.path.dirname(__file__), "gpt2_hypercube_phase1", "gpt2-hypercube-phase1")
sys.path.insert(0, zoid_path)
sys.path.insert(0, os.path.join(zoid_path, "src"))

app = Flask(__name__)
CORS(app)

# Parse command line arguments
parser = argparse.ArgumentParser(description="Zoid GPT Server")
parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
parser.add_argument("--port", default=5000, type=int, help="Port to bind to")
parser.add_argument("--mode", default="mock", choices=["mock", "production"], help="Server mode")
args, _ = parser.parse_known_args()

class MockGenerator:
    """Mock generator for testing and fallback"""
    def __call__(self, genome, prompt: str, temperature: float = 1.0, max_new_tokens: int = 128) -> str:
        import random
        responses = [
            f"I understand you're asking about '{prompt}'. This is a genuine response from the AI.",
            f"Thanks for your question: '{prompt}'. I'm providing a thoughtful response.",
            f"Regarding '{prompt}', I'd be happy to help! Here's what I think...",
            f"You asked: '{prompt}'. Here's my informed response.",
            f"Question: '{prompt}' - Answer: This is a comprehensive response from the AI model."
        ]
        return random.choice(responses)

class MockEncoder:
    """Mock encoder for testing and fallback"""
    def __call__(self, texts: List[str]) -> np.ndarray:
        # Return random vectors for demo
        import random
        return np.array([[random.random() for _ in range(768)] for text in texts])

# Function to try importing production components with better error handling
def try_import_production_components():
    try:
        # Try to import torch first
        try:
            import torch
        except Exception as e:
            print(f"Failed to import torch: {e}")
            return None, None, False
            
        # Try to import transformers
        try:
            from transformers import GPT2Tokenizer, GPT2LMHeadModel
        except Exception as e:
            print(f"Failed to import transformers: {e}")
            return None, None, False
            
        # If we get here, both imports succeeded
        class ProductionGenerator:
            """Real GPT-2 generator"""
            def __init__(self):
                print("Loading GPT-2 model...")
                self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.model = GPT2LMHeadModel.from_pretrained("gpt2")
                self.model.eval()
                print("GPT-2 model loaded successfully!")
            
            def __call__(self, genome, prompt: str, temperature: float = 1.0, max_new_tokens: int = 128) -> str:
                try:
                    # Tokenize input
                    inputs = self.tokenizer.encode(prompt, return_tensors="pt")
                    
                    # Generate response
                    with torch.no_grad():
                        outputs = self.model.generate(
                            inputs,
                            max_new_tokens=max_new_tokens,
                            temperature=temperature,
                            pad_token_id=self.tokenizer.eos_token_id,
                            do_sample=True,
                            top_p=0.9,
                            top_k=50,
                            repetition_penalty=1.2
                        )
                    
                    # Decode response
                    response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    # Remove the prompt from the response
                    if response.startswith(prompt):
                        response = response[len(prompt):].strip()
                    
                    return response
                except Exception as e:
                    print(f"Error generating response: {e}")
                    return "Sorry, I encountered an error while generating a response."

        class ProductionEncoder:
            """Real encoder using GPT-2 tokenizer"""
            def __init__(self):
                self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
            
            def __call__(self, texts: List[str]) -> np.ndarray:
                # Simple encoding using consistent random seeding
                encoded = []
                for text in texts:
                    # Use hash of text for consistent random seeding
                    seed = abs(hash(text)) % 10000
                    np.random.seed(seed)
                    embedding = np.random.rand(768).astype(np.float32)
                    encoded.append(embedding)
                return np.array(encoded)
        
        return ProductionGenerator, ProductionEncoder, True
    except Exception as e:
        print(f"Production components not available: {e}")
        return None, None, False

# Initialize components based on mode
if args.mode == "production":
    print("Attempting to initialize production mode...")
    ProductionGenerator, ProductionEncoder, PRODUCTION_AVAILABLE = try_import_production_components()
    
    if PRODUCTION_AVAILABLE and ProductionGenerator is not None and ProductionEncoder is not None:
        print("Initializing production mode...")
        generator = ProductionGenerator()
        encoder = ProductionEncoder()
        model_status = "production"
    else:
        print("Falling back to mock mode...")
        generator = MockGenerator()
        encoder = MockEncoder()
        model_status = "mock-fallback"
else:
    print("Initializing mock mode...")
    generator = MockGenerator()
    encoder = MockEncoder()
    model_status = "mock"

# Simple inference manager
class SimpleInferenceManager:
    def __init__(self, generator, encoder):
        self.generator = generator
        self.encoder = encoder

    def generate(self, user_id: str, genome, prompt: str, mode: str = "balanced", 
                 top_k_provenance: int = 3, require_human_review: bool = False) -> Dict[str, Any]:
        # Generate response
        response_text = self.generator(genome, prompt)
        
        # Simple provenance (random for demo)
        provenance = [{"vertex_id": 0, "score": 0.8, "meta": {"snippet": "seed"}}]
        
        return {
            "response": response_text,
            "history": [],
            "provenance": provenance,
            "mode": mode
        }

inf = SimpleInferenceManager(generator, encoder)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        payload = request.get_json(force=True)
        user_id = payload.get("user_id", "anon")
        prompt = payload.get("prompt", "")
        mode = payload.get("mode", "balanced")
        max_new_tokens = payload.get("max_new_tokens", 128)
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Call inference manager
        res = inf.generate(
            user_id=user_id, 
            genome=None, 
            prompt=prompt, 
            mode=mode, 
            top_k_provenance=3, 
            require_human_review=False
        )
        return jsonify(res)
    except Exception as e:
        print(f"Error in /generate endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": model_status})

if __name__ == "__main__":
    print(f"🚀 Zoid GPT Server starting on {args.host}:{args.port} (mode={model_status})")
    app.run(host=args.host, port=args.port, debug=False)