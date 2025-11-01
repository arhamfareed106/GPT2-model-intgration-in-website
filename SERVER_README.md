# Zoid GPT Server

This is the backend server for the Zoid GPT project. It provides a REST API for generating text using either a mock implementation or a real GPT-2 model.

## Features

- REST API with `/generate` and `/health` endpoints
- Support for both mock mode (for testing) and production mode (with real GPT-2 model)
- CORS support for web frontend integration
- Configurable host and port

## Requirements

### For Mock Mode (Default):
- Python 3.7+
- Flask
- NumPy

### For Production Mode:
- All mock mode requirements, plus:
- PyTorch
- Transformers (Hugging Face)
- GPT-2 model access

## Installation

1. Install the required packages:
   ```bash
   pip install flask numpy
   ```

2. For production mode, also install:
   ```bash
   pip install torch transformers
   ```

## Usage

### Start the Server

#### Mock Mode (default):
```bash
python scripts/final_server.py --host 0.0.0.0 --port 5000
```

#### Production Mode:
```bash
python scripts/final_server.py --mode production --host 0.0.0.0 --port 5000
```

### API Endpoints

#### Health Check
```
GET /health
```

Response:
```json
{
  "status": "ok",
  "model": "mock" or "production"
}
```

#### Generate Text
```
POST /generate
```

Request Body:
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

## Error Handling

The server includes proper error handling:
- Returns appropriate HTTP status codes
- Provides error messages in JSON format
- Falls back to mock mode if production dependencies are not available

## Development

To test the server, you can use the provided `test_api.py` script:
```bash
python test_api.py
```

This will test both the health check and generate endpoints.