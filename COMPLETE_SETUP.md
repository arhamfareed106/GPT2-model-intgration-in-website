# Zoid GPT Complete Setup Guide

This guide explains how to set up and run the Zoid GPT system with real AI inference.

## System Architecture

The Zoid GPT system consists of:
1. **Backend Server**: Flask API that handles AI inference
2. **Frontend Interface**: React-based chat interface
3. **AI Model**: GPT-2 based model with quantization for efficiency

## Installation Steps

### 1. Install Required System Dependencies (Windows)

On Windows, you may need to install the Microsoft Visual C++ Redistributable to avoid DLL loading errors:

1. Download and install Microsoft Visual C++ Redistributable from:
   https://aka.ms/vs/17/release/vc_redist.x64.exe

### 2. Install Python Dependencies

Navigate to your project directory and install the required Python packages:

```bash
# Upgrade pip to the latest version
python -m pip install --upgrade pip

# Install core dependencies
pip install flask numpy torch transformers

# Install additional project dependencies
pip install -r gpt2_hypercube_phase1/gpt2-hypercube-phase1/requirements.txt
```

### 3. Verify Installation

Check that all required packages are installed:

```bash
pip list | grep -E "(torch|transformers|flask|numpy)"
```

You should see entries for:
- torch
- transformers
- flask
- numpy

## Running the System

### Start the Backend Server

#### Mock Mode (Default - for testing)
```bash
python scripts/local_server.py --host 0.0.0.0 --port 5000
```

#### Production Mode (Real AI Inference)
```bash
python scripts/local_server.py --mode production --host 0.0.0.0 --port 5000
```

### Start the Frontend Interface

```bash
cd frontend
python -m http.server 3000
```

## Using the System

### Web Interface

1. Open your browser and navigate to http://localhost:3000
2. Type your questions in the chat interface
3. Receive AI-generated responses in real-time

### Direct API Usage

You can also interact with the API directly:

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Generate Text
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?", "user_id": "test_user"}'
```

### Programmatic Usage

You can import and use the `generate_response` function directly in your Python code:

```python
from scripts.local_server import generate_response

# Generate a response
response = generate_response("What is the capital of France?")
print(response)
```

## API Endpoints

### GET /health
Returns server status and current mode.

Response:
```json
{
  "status": "ok",
  "model": "production" or "mock"
}
```

### POST /generate
Generates text based on a prompt.

Request:
```json
{
  "prompt": "Your prompt here",
  "user_id": "optional_user_id",
  "mode": "balanced",
  "max_new_tokens": 128
}
```

Response:
```json
{
  "response": "Generated text response"
}
```

## Configuration

The server accepts the following command-line arguments:

- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to bind to (default: 5000)
- `--mode`: Server mode, either "mock" or "production" (default: mock)

## Model Features

### Production Mode
- Uses real GPT-2 model for text generation
- Supports quantized models for efficiency
- Provides authentic AI responses
- Temperature control for response creativity

### Mock Mode
- Returns simulated AI responses
- No ML dependencies required
- Useful for testing and development

## Troubleshooting

### Common Issues

1. **DLL Load Failure on Windows**
   - Error: `[WinError 126] The specified module could not be found`
   - Solution: Install Microsoft Visual C++ Redistributable

2. **Import Errors**
   - Error: `No module named 'torch'` or similar
   - Solution: Reinstall the missing packages with `pip install torch transformers`

3. **CUDA Out of Memory**
   - Error: `CUDA out of memory`
   - Solution: The model will automatically fall back to CPU processing

### Testing the System

You can test the system using the provided test scripts:

```bash
# Test API endpoints
python test_api.py

# Test generate_response function
python test_generate_response.py

# Verify model uniqueness
python verify_model.py
```

## Performance Considerations

1. **First Run**: The first time you run in production mode, the GPT-2 model will be downloaded (approximately 500MB)
2. **Memory Usage**: The model requires approximately 1-2GB of RAM
3. **Response Time**: First inference may take a few seconds; subsequent requests are faster

## Security Notes

- The server includes CORS support for web frontend integration
- In production, consider adding authentication and rate limiting
- The development server should not be used in production environments

## Example Usage

Try these example prompts to test the system:

1. "What is the capital of France?"
2. "How many continents are there in the world?"
3. "Explain quantum computing in simple terms"
4. "Write a short poem about spring"
5. "What is the tallest mountain in the world?"

Each prompt should generate a unique, contextually appropriate response from the AI model.