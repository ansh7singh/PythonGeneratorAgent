# AI Coding Agent

A full-stack AI coding agent application powered by Google's Gemini 2.0. This application provides an intelligent assistant that can perform file operations, read/write files, and execute Python scripts through a modern web interface.

## Features

- 🤖 **AI-Powered Assistant**: Uses Gemini 2.0 Flash for intelligent code assistance
- 📁 **File Operations**: List, read, and write files
- 🐍 **Python Execution**: Run Python scripts with arguments
- 💬 **Modern Chat Interface**: Beautiful React-based chat UI
- 🔧 **Function Call Visualization**: See what operations the AI is performing
- 📊 **Token Usage Tracking**: Monitor API usage

## Project Structure

```
.
├── aiagent/              # Backend Python application
│   ├── api_server.py     # FastAPI server
│   ├── main.py           # CLI version
│   ├── functions1/       # Function implementations
│   └── call_function.py  # Function dispatcher
└── frontend/             # React frontend
    ├── src/
    │   ├── App.tsx       # Main React component
    │   ├── api.ts        # API client
    │   └── types.ts      # TypeScript types
    └── package.json
```

## Prerequisites

- Python 3.13+
- Node.js 18+
- Google Gemini API key

## Setup

### 1. Backend Setup

1. Navigate to the backend directory:
```bash
cd aiagent
```

2. Install dependencies (using uv or pip):
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

3. Create a `.env` file in the `aiagent` directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Start the API server:
```bash
python api_server.py
```

The API will be available at `http://localhost:8000`

### 2. Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. (Optional) Create a `.env` file if you need to change the API URL:
```env
VITE_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. Start the backend server (in `aiagent/` directory)
2. Start the frontend server (in `frontend/` directory)
3. Open `http://localhost:3000` in your browser
4. Start chatting with the AI agent!

### Example Queries

- "List all files in the current directory"
- "Read the content of main.py"
- "Create a new file called test.txt with the content 'Hello World'"
- "Run the calculator/main.py file"

## API Endpoints

### `POST /chat`
Send a message to the AI agent.

**Request:**
```json
{
  "message": "List files in the current directory",
  "conversation_history": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help you?"
    }
  ]
}
```

**Response:**
```json
{
  "response": "Here are the files...",
  "function_calls": [
    {
      "name": "get_files_info",
      "args": {"directory": "."},
      "result": "- file1.py: file_size=1234, is_dir=false"
    }
  ],
  "usage_metadata": {
    "prompt_token_count": 100,
    "candidates_token_count": 50,
    "total_token_count": 150
  }
}
```

### `GET /health`
Health check endpoint.

## Development

### Backend

The backend uses FastAPI. You can run it with:
```bash
python api_server.py
```

Or with uvicorn directly:
```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

The frontend uses Vite for fast development. Run:
```bash
npm run dev
```

Build for production:
```bash
npm run build
```

## Technologies

### Backend
- FastAPI - Modern Python web framework
- Google Gemini API - AI model
- Uvicorn - ASGI server

### Frontend
- React 18 - UI library
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- Axios - HTTP client

## Security Notes

- All file operations are constrained to the working directory
- Path traversal attempts are blocked
- API keys should be stored in environment variables, never committed to git

## License

MIT

