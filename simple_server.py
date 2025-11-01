import os
import json
import argparse
from typing import List, Dict, Any
from flask import Flask, request, jsonify

# Simple in-memory vectordb
class SimpleVectorDB:
    def __init__(self, dim: int = 128):
        self.dim = dim
        self._vecs = []  # list of (id, vec, meta)
    
    def upsert(self, vid: int, vec: List[float], meta: Dict[str, Any] = None):
        self._vecs.append({"vertex_id": int(vid), "vec": vec, "score": 1.0, "meta": meta or {}})
    
    def query(self, qvec: List[float], top_k: int = 3):
        if len(self._vecs) == 0:
            return []
        # Simple similarity (just return first items for demo)
        out = []
        for i, e in enumerate(self._vecs[:top_k]):
            out.append({"vertex_id": e["vertex_id"], "score": 1.0 - i*0.1, "meta": e["meta"]})
        return out

# Mock generator function
def mock_generator(genome, prompt: str, temperature: float = 1.0, max_new_tokens: int = 128) -> str:
    responses = [
        f"I understand you're asking about '{prompt}'. This is a mock response from the AI.",
        f"Thanks for your prompt: '{prompt}'. In a real implementation, I would generate a detailed response.",
        f"Regarding '{prompt}', I'd be happy to help! This is a simulated response."
    ]
    import random
    return random.choice(responses)

# Mock encoder function
def mock_encoder(texts: List[str]) -> List[List[float]]:
    # Return random vectors for demo
    import random
    return [[random.random() for _ in range(128)] for _ in texts]

# Flask app
app = Flask(__name__)
parser = argparse.ArgumentParser()
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", default=5000, type=int)
args, _ = parser.parse_known_args()

# Initialize components
vdb = SimpleVectorDB(dim=128)
# Seed vectordb with a dummy vertex
vdb.upsert(0, [0.1] * 128, {"snippet": "seed"})

class DialogueState:
    def __init__(self, capacity: int = 16):
        self.capacity = capacity
        self.states = {}
    
    def update(self, user_id: str, prompt: str, response: str):
        if user_id not in self.states:
            self.states[user_id] = []
        self.states[user_id].append({"prompt": prompt, "response": response})
        if len(self.states[user_id]) > self.capacity:
            self.states[user_id].pop(0)
    
    def get_history(self, user_id: str):
        return self.states.get(user_id, [])

class InferenceManager:
    def __init__(self, generator, encoder, vectordb, dialogue_state):
        self.generator = generator
        self.encoder = encoder
        self.vectordb = vectordb
        self.dialogue_state = dialogue_state
    
    def generate(self, user_id: str, genome, prompt: str, mode: str = "balanced", 
                 top_k_provenance: int = 3, require_human_review: bool = False) -> Dict[str, Any]:
        # Generate response
        response_text = self.generator(genome, prompt)
        
        # Update dialogue state
        self.dialogue_state.update(user_id, prompt, response_text)
        
        # Get history
        history = self.dialogue_state.get_history(user_id)
        
        # Encode prompt and query vector db
        prompt_vec = self.encoder([prompt])[0]
        provenance = self.vectordb.query(prompt_vec, top_k=top_k_provenance)
        
        return {
            "response": response_text,
            "history": history,
            "provenance": provenance,
            "mode": mode
        }

dialogue_state = DialogueState(capacity=16)
inf = InferenceManager(generator=mock_generator, encoder=mock_encoder, vectordb=vdb, dialogue_state=dialogue_state)

@app.route("/generate", methods=["POST"])
def generate():
    payload = request.get_json(force=True)
    user_id = payload.get("user_id", "anon")
    prompt = payload.get("prompt", "")
    mode = payload.get("mode", "balanced")
    max_new_tokens = payload.get("max_new_tokens", 128)
    
    # Call inference manager
    res = inf.generate(user_id=user_id, genome=None, prompt=prompt, mode=mode, top_k_provenance=3, require_human_review=False)
    return jsonify(res)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "mock"})

if __name__ == "__main__":
    print(f"Starting server on {args.host}:{args.port} (model=mock)")
    app.run(host=args.host, port=args.port, debug=True)
