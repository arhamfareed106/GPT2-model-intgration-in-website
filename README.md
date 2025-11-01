# 🤖 Zoid - Advanced GPT-2 Chat Application

A sophisticated web-based chat application powered by a fine-tuned GPT-2 model with advanced features for natural language processing and interactive conversations.

## 🌟 Features

- **Advanced GPT-2 Integration**: Custom-trained GPT-2 model with enhanced response generation
- **Interactive Chat Interface**: Modern React-based frontend with real-time responses
- **Robust Backend Architecture**: Flask-based server with optimized model inference
- **Multi-Mode Generation**: Supports different conversation modes (balanced, creative, precise)
- **Production-Ready**: Includes configuration for deployment and scalability
- **Comprehensive Testing**: Extensive test suite covering all components
- **Model Distillation**: Optimized model performance through knowledge distillation
- **Frontend Technologies**:
  - React + Vite for lightning-fast development
  - Tailwind CSS for modern, responsive design
  - Real-time chat updates and message history

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip package manager
- npm package manager

### Backend Setup
```bash
# Install Python dependencies
python -m pip install --upgrade pip
pip install -r gpt2-hypercube-phase1/requirements.txt
pip install flask transformers torch

# Run the server
python scripts/local_server.py --host 0.0.0.0 --port 5000
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔧 Project Structure

```
├── frontend/               # React frontend application
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   └── assets/       # Static assets
├── src/                   # Core Python package
├── scripts/               # Server implementations
├── tests/                # Comprehensive test suite
└── gpt2_hypercube_phase1/ # Model training and optimization
```

## 🧪 Testing

The project includes extensive testing coverage:
```bash
# Run all tests
pytest -q

# Run specific test suites
pytest -q gpt2-hypercube-phase1/tests/test_inference.py
```

## 🛠️ API Endpoints

### Generate Response
```http
POST /generate
Content-Type: application/json

{
    "user_id": "user123",
    "prompt": "Your message here",
    "mode": "balanced",
    "max_new_tokens": 50
}
```

## 🎯 Key Features

1. **Model Optimization**
   - Custom model distillation pipeline
   - Efficient inference optimization
   - Memory usage optimization

2. **Frontend Features**
   - Real-time chat interface
   - Message history
   - Response streaming
   - Multiple chat modes

3. **Backend Capabilities**
   - Robust error handling
   - Request validation
   - Performance monitoring
   - Scalable architecture

## 📈 Performance

- Fast response generation
- Optimized model loading
- Efficient memory usage
- Scalable architecture for production deployment

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for the base GPT-2 model
- Hugging Face for transformer implementations
- The open-source community for various tools and libraries

---

Made with ❤️ by [arhamfareed106](https://github.com/arhamfareed106)
