# Zoid GPT Frontend

A modern React-based chat interface for the Zoid GPT project.

## Features

- Real-time chat interface with the Zoid GPT model
- Responsive design that works on desktop and mobile
- Dark/light mode toggle
- Server status indicator
- Message history with timestamps
- Loading indicators while waiting for responses
- Clear chat functionality

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- The Zoid GPT backend server running

## Setup Instructions

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser to http://localhost:3000

## Backend Connection

The frontend expects the backend to be running at `http://127.0.0.1:5000`. Make sure to start the backend server before using the frontend:

```bash
cd ..
python scripts/local_server.py --host 0.0.0.0 --port 5000
```

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── ChatInput.jsx
│   │   ├── ChatWindow.jsx
│   │   └── Header.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── vite.config.js
└── README.md
```

## Development

To build for production:
```bash
npm run build
```

To preview the production build:
```bash
npm run preview
```

## Technologies Used

- React 18
- Vite
- Tailwind CSS
- JavaScript (ES6+)