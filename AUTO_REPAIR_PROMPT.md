# 🧩 Zoid GPT Auto-Repair Prompt: Fix Model – Auto Real Inference Mode

You are an expert Python AI engineer fixing the Zoid GPT project's inference pipeline.

## Objective

Automatically repair the inference system so it switches from mock/demo mode to fully functional GPT-2 text generation.

## Current Issue

- Model replies like "mn, say in the format 'The ['" or "The capital of gharb".
- This means the inference layer runs, but model weights and tokenizer are missing or corrupted.
- The quantized model (in src/core/quantized_gpt2.py) or load function is misconfigured.

## Steps to Auto-Fix

### 1. ✅ Reinstall all required dependencies

```bash
pip install torch transformers accelerate sentencepiece
```

### 2. ✅ Open the file

```
src/deployment/inference.py
```

or any function that handles `generate()` or `run_inference()`.

### 3. Replace the mock/quantized load logic with the **real GPT-2** initialization

```python
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

print("🔧 Loading GPT2 model and tokenizer...")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")
model.eval()

def run_inference(prompt: str):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_length=120,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### 4. ✅ Ensure the Flask API route in `scripts/local_server.py` uses this real inference function

```python
from src.deployment.inference import run_inference

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")
    result = run_inference(prompt)
    return jsonify({"response": result})
```

### 5. ✅ Test the live inference

```bash
python scripts/local_server.py --host 0.0.0.0 --port 5000
```

### 6. Open another terminal or browser

```bash
curl -X POST http://127.0.0.1:5000/generate -H "Content-Type: application/json" -d "{\"prompt\": \"capital of Pakistan\"}"
```

Expected output:

```json
{
  "response": "The capital of Pakistan is Islamabad."
}
```

### 7. ✅ Confirm multiple tests

```python
print(run_inference("world largest country in area"))
print(run_inference("capital of Italy"))
print(run_inference("history of America in 12 words"))
```

If results are fluent, factual, and different per question → success!

### 8. (Optional) 🔄 Re-enable quantization later for optimization once the real inference mode works perfectly.

## Final Goal

* Model generates meaningful text, not placeholders.
* API `/generate` route responds intelligently to real prompts.
* No undefined or random "gharb / mn" type text.
* Zero Python, path, or import errors.

## 🌐 Simple HTML Chat Frontend

To test the fixed model with a simple web interface, create `simple_chat.html` with the following content:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zoid GPT - Simple Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #1a2a6c, #b21f1f, #1a2a6c);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        h1 {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1rem;
            opacity: 0.8;
        }
        
        .chat-container {
            height: 500px;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            max-width: 80%;
            padding: 15px;
            border-radius: 18px;
            position: relative;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            align-self: flex-end;
            background: #3498db;
            color: white;
            border-bottom-right-radius: 5px;
        }
        
        .ai-message {
            align-self: flex-start;
            background: #ecf0f1;
            border-bottom-left-radius: 5px;
        }
        
        .typing-indicator {
            align-self: flex-start;
            background: #ecf0f1;
            padding: 15px;
            border-radius: 18px;
            border-bottom-left-radius: 5px;
            display: none;
        }
        
        .typing-indicator span {
            height: 10px;
            width: 10px;
            float: left;
            margin: 0 2px;
            background-color: #9E9EA1;
            display: block;
            border-radius: 50%;
            opacity: 0.4;
        }
        
        .typing-indicator span:nth-of-type(1) {
            animation: typing 1s infinite;
        }
        
        .typing-indicator span:nth-of-type(2) {
            animation: typing 1s infinite 0.2s;
        }
        
        .typing-indicator span:nth-of-type(3) {
            animation: typing 1s infinite 0.4s;
        }
        
        @keyframes typing {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        
        .input-container {
            display: flex;
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #eee;
        }
        
        #user-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 30px;
            outline: none;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        #user-input:focus {
            border-color: #3498db;
        }
        
        #send-button {
            background: #3498db;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            margin-left: 15px;
            cursor: pointer;
            transition: background 0.3s;
            font-size: 1.2rem;
        }
        
        #send-button:hover {
            background: #2980b9;
        }
        
        .info-panel {
            background: #e8f4fc;
            padding: 15px;
            text-align: center;
            font-size: 0.9rem;
            color: #2c3e50;
        }
        
        .test-queries {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-top: 10px;
        }
        
        .test-query {
            background: #d6eaf8;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .test-query:hover {
            background: #aed6f1;
        }
        
        @media (max-width: 600px) {
            .container {
                border-radius: 10px;
            }
            
            .chat-container {
                height: 400px;
                padding: 15px;
            }
            
            h1 {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Zoid GPT Chat</h1>
            <div class="subtitle">Real GPT-2 Inference Mode</div>
        </header>
        
        <div class="chat-container" id="chat-container">
            <div class="message ai-message">
                Hello! I'm Zoid, your AI assistant. Ask me anything about countries, capitals, history, or general knowledge!
            </div>
            <div class="message ai-message">
                Try questions like:
                <div class="test-queries">
                    <div class="test-query" onclick="sendTestQuery('capital of Pakistan')">capital of Pakistan</div>
                    <div class="test-query" onclick="sendTestQuery('world largest country in area')">world largest country in area</div>
                    <div class="test-query" onclick="sendTestQuery('capital of Italy')">capital of Italy</div>
                </div>
            </div>
            <div class="typing-indicator" id="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Type your message here..." autocomplete="off">
            <button id="send-button" onclick="sendMessage()">➤</button>
        </div>
        
        <div class="info-panel">
            <p>Powered by Real GPT-2 Inference | Responses are generated in real-time</p>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        const typingIndicator = document.getElementById('typing-indicator');
        
        // Focus on input field when page loads
        window.onload = () => {
            userInput.focus();
        };
        
        // Send message when Enter is pressed
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        function addMessage(text, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function sendTestQuery(query) {
            userInput.value = query;
            sendMessage();
        }
        
        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, true);
            userInput.value = '';
            
            // Show typing indicator
            typingIndicator.style.display = 'block';
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            try {
                // Call the API
                const response = await fetch('http://127.0.0.1:5000/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        prompt: message,
                        user_id: 'web_user'
                    })
                });
                
                const data = await response.json();
                
                // Hide typing indicator
                typingIndicator.style.display = 'none';
                
                // Add AI response to chat
                const reply = data.reply || data.response || "Sorry, I couldn't generate a response.";
                addMessage(reply);
            } catch (error) {
                // Hide typing indicator
                typingIndicator.style.display = 'none';
                
                // Add error message to chat
                addMessage("Sorry, I encountered an error. Please make sure the backend server is running.");
                console.error('Error:', error);
            }
        }
    </script>
</body>
</html>
```

## 🚀 How to Use the Complete Solution

1. Save the HTML code above as `simple_chat.html`
2. Start your backend server:
   ```bash
   python scripts/local_server.py --mode production
   ```
3. Open `simple_chat.html` in your web browser
4. Start chatting with your fixed Zoid GPT model!

The frontend will automatically connect to your backend at `http://127.0.0.1:5000` and send requests to the `/generate` endpoint.