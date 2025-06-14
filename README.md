# Voice Agent Backend

This backend provides APIs for managing voice agent calls and runs a LiveKit agent worker.

## Quick Start

### Option 1: Run Both Services Together (Recommended for Development)
```bash
cd backend
python run_dev.py
```

This will start:
- FastAPI server at `http://localhost:8000`
- API documentation at `http://localhost:8000/docs`
- LiveKit agent worker connected to your LiveKit server

### Option 2: Run Services Separately

**Terminal 1 - FastAPI Server:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - LiveKit Worker:**
```bash
cd backend
python worker.py
```

## Environment Variables

Make sure you have these environment variables set in your `.env` file:

```env
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
LIVEKIT_TRUNK_ID=your_trunk_id
GROQ_API_KEY=your_groq_api_key
```

## API Endpoints

- `POST /api/v1/start-call` - Start a new voice agent call
- `GET /docs` - Interactive API documentation

## Architecture

- `main.py` - FastAPI application with REST APIs
- `worker.py` - LiveKit agent worker that handles voice calls
- `run_dev.py` - Development script to run both services
- `app/services/livekit_process.py` - LiveKit agent implementation
- `app/api/` - API route handlers 