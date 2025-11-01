# Running Zoid GPT Application

## Prerequisites

1. Python 3.8 or higher
2. Node.js and npm (for frontend development)
3. Install required Python packages:
   ```
   pip install -r gpt2-hypercube-phase1/gpt2-hypercube-phase1/requirements.txt
   pip install flask transformers torch
   ```

## Running the Backend Server

1. Navigate to the project root directory:
   ```
   cd c:\Users\muSA\Downloads\Compressed\New folder\add frontend\Zoid-main
   ```

2. Run the backend server:
   ```
   python scripts/local_server.py --mode mock
   ```
   
   For production mode with real GPT-2 model:
   ```
   python scripts/local_server.py --mode production
   ```

3. The server will start on `http://127.0.0.1:5000`

## Running the Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Open your browser and go to `http://localhost:3000`

## Testing the API

You can test the API directly using curl:

```bash
curl -X POST http://127.0.0.1:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?", "user_id": "test_user"}'
```

## Troubleshooting

1. **Port already in use**: If you get an error about the port being in use, kill any existing Python processes:
   ```
   taskkill /f /im python.exe
   ```

2. **CORS issues**: The backend already has CORS enabled for localhost:3000.

3. **Model loading issues**: On Windows, make sure you have Microsoft Visual C++ Redistributable installed.

4. **Node.js not found**: Install Node.js from https://nodejs.org/