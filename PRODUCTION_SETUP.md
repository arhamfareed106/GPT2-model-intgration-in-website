# Zoid GPT Production Setup Guide

This guide explains how to set up and run the Zoid GPT server in production mode with real GPT-2 model inference.

## Prerequisites

1. Python 3.7 or higher
2. pip package manager
3. Git (for cloning the repository)

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
pip install flask numpy

# Install PyTorch and Transformers for production mode
pip install torch transformers

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

## Running the Server

### Mock Mode (Default)
```bash
python scripts/robust_server.py --host 0.0.0.0 --port 5000
```

### Production Mode
```bash
python scripts/robust_server.py --mode production --host 0.0.0.0 --port 5000
```

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

### Testing the Server

You can test the server using the provided test script:

```bash
python test_api.py
```

Or manually with curl:

```bash
# Health check
curl http://localhost:5000/health

# Generate text
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?", "user_id": "test_user"}'
```

## Server Modes

### Mock Mode
- Returns simulated AI responses
- No ML dependencies required
- Useful for testing and development

### Production Mode
- Uses real GPT-2 model for text generation
- Requires PyTorch and Transformers
- Provides authentic AI responses

The server will automatically fall back to mock mode if production dependencies are not available.

## API Endpoints

### GET /health
Returns server status and current mode.

Response:
```json
{
  "status": "ok",
  "model": "production" or "mock" or "mock-fallback"
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
  "response": "Generated text response",
  "history": [],
  "provenance": [
    {
      "vertex_id": 0,
      "score": 0.8,
      "meta": {
        "snippet": "seed"
      }
    }
  ],
  "mode": "balanced"
}
```

## Configuration

The server accepts the following command-line arguments:

- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to bind to (default: 5000)
- `--mode`: Server mode, either "mock" or "production" (default: mock)

## Performance Considerations

1. **First Run**: The first time you run in production mode, the GPT-2 model will be downloaded (approximately 500MB)
2. **Memory Usage**: The model requires approximately 1-2GB of RAM
3. **Response Time**: First inference may take a few seconds; subsequent requests are faster

## Security Notes

- The server includes CORS support for web frontend integration
- In production, consider adding authentication and rate limiting
- The development server should not be used in production environments