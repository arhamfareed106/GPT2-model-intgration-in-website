#!/usr/bin/env python3
"""
Zoid GPT Server - Production Mode
This server uses the actual GPT-2 model with Zoid framework components.
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
sys.path.append(zoid_path)

# Initialize these variables to None to avoid linter errors
DialogueState = None
InferenceManager = None
VectorDB = None
basic_safety_check = None
fallback_safe_response = None

try:
    from src.deployment.dialogue_state import DialogueState
    from src.deployment.inference import InferenceManager
    from src.knowledge.vector_db import VectorDB
    from src.deployment.safety import basic_safety_check, fallback_safe_response
except ImportError as e:
    print(f"Warning: Could not import Zoid modules: {e}")
    # Fallback to simple implementation if Zoid modules are not available

app = Flask(__name__)
CORS(app)

# Parse command line arguments
parser = argparse.ArgumentParser(description="Zoid GPT Server")
parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
parser.add_argument("--port", default=5000, type=int, help="Port to bind to")
parser.add_argument("--mode", default="production", choices=["mock", "production"], help="Server mode")
args, _ = parser.parse_known_args()

# Only import PyTorch and transformers when needed (in production mode)
if args.mode == "production":
    try:
        import torch
        from transformers import GPT2Tokenizer, GPT2LMHeadModel
        
        class GPT2Generator:
            """Wrapper for GPT-2 model to match the expected interface"""
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

        class GPT2Encoder:
            """Wrapper for GPT-2 tokenizer to create embeddings"""
            def __init__(self):
                self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
                # We don't need to load the full model for encoding in this simple implementation
                # The tokenizer is sufficient for basic text processing
            
            def __call__(self, texts: List[str]) -> np.ndarray:
                try:
                    # Simple approach: create random embeddings with consistent seeding
                    encoded = []
                    for text in texts:
                        # Use hash of text for consistent random seeding
                        seed = abs(hash(text)) % 10000
                        np.random.seed(seed)
                        embedding = np.random.rand(768).astype(np.float32)
                        encoded.append(embedding)
                    return np.array(encoded)
                except Exception as e:
                    print(f"Error encoding text: {e}")
                    # Return random vectors as fallback
                    return np.random.rand(len(texts), 768)
    except ImportError as e:
        print(f"Failed to import PyTorch/Transformers: {e}")
        print("Falling back to mock mode...")
        args.mode = "mock"

# Mock mode implementations
def mock_generator(genome, prompt: str, temperature: float = 1.0, max_new_tokens: int = 128) -> str:
    responses = [
        f"I understand you're asking about '{prompt}'. This is a response from the AI.",
        f"Thanks for your question: '{prompt}'. I'm providing a helpful response.",
        f"Regarding '{prompt}', I'd be happy to help! Here's what I think...",
        f"You asked: '{prompt}'. Here's my response based on my knowledge.",
        f"Question: '{prompt}' - Answer: This is a thoughtful response from the AI model."
    ]
    import random
    return random.choice(responses)

def mock_encoder(texts: List[str]) -> np.ndarray:
    # Return random vectors for demo
    import random
    return np.array([[random.random() for _ in range(768)] for _ in texts])

# Initialize components based on mode
if args.mode == "production":
    print("Initializing production mode with real GPT-2 model...")
    try:
        generator = GPT2Generator()
        encoder = GPT2Encoder()
        model_status = "production"
    except Exception as e:
        print(f"Failed to initialize GPT-2 model: {e}")
        print("Falling back to mock mode...")
        args.mode = "mock"
        model_status = "mock-fallback"

if args.mode == "mock":
    print("Initializing mock mode...")
    generator = mock_generator
    encoder = mock_encoder
    model_status = "mock"

# Initialize Zoid components
dialogue_state = None
vectordb = None
inf = None

try:
    if DialogueState and VectorDB and InferenceManager:
        dialogue_state = DialogueState(capacity=16)
        vectordb = VectorDB()
        # Seed vectordb with a dummy vertex
        vectordb.upsert(0, np.random.rand(768).astype(np.float32), {"snippet": "seed"})
        
        # Initialize inference manager
        inf = InferenceManager(
            generator=generator,
            encoder=encoder,
            vectordb=vectordb,
            dialogue_state=dialogue_state
        )
        print("Zoid components initialized successfully!")
    else:
        raise ImportError("Zoid components not available")
except Exception as e:
    print(f"Warning: Could not initialize Zoid components: {e}")
    # Fallback implementation
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
    print("Using fallback inference manager.")

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