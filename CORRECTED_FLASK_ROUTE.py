"""
Sample corrected Flask route code for the /generate endpoint.
This code ensures that the endpoint always returns a valid JSON response.
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        # Ensure we have valid JSON
        if not request.is_json:
            return jsonify({"reply": "Invalid request format. Please send JSON."}), 400
            
        payload = request.get_json(force=True)
        
        # Extract parameters with defaults
        user_id = payload.get("user_id", "anon")
        prompt = payload.get("prompt", "").strip()
        mode = payload.get("mode", "balanced")
        max_new_tokens = payload.get("max_new_tokens", 30)
        
        # Validate prompt
        if not prompt:
            return jsonify({"reply": "Please provide a prompt."}), 400
            
        # Call your model inference function here
        # For example:
        # generated_text = your_model_inference_function(prompt)
        
        # Placeholder for actual model inference
        # In a real implementation, replace this with your actual model call
        generated_text = "The capital of Pakistan is Islamabad."  # Example response
        
        # Handle empty or None responses
        if not generated_text or not generated_text.strip():
            generated_text = "I'm not sure."
            
        # Ensure we return a valid JSON response
        return jsonify({"reply": generated_text.strip()})
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error in generate endpoint: {e}")
        # Always return a valid JSON response
        return jsonify({"reply": "I'm not sure."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)