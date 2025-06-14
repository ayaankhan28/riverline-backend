# Voice Agent Backend - Integrated Setup

This backend provides APIs for managing voice agent calls and runs a LiveKit agent worker **integrated directly within FastAPI**. Now includes real-time WebSocket support for live transcriptions!

## ✨ Features

- **Integrated LiveKit Worker**: No separate processes needed - everything runs in one FastAPI application
- **Real-time WebSocket Support**: Get live transcriptions and call status updates
- **RESTful API**: Start calls and manage agent interactions
- **Call Tracking**: Each call gets a unique ID for WebSocket connections
- **Graceful Shutdown**: Proper cleanup of LiveKit worker and WebSocket connections

## 🚀 Quick Start

### Prerequisites

Make sure you have these environment variables in your `.env` file:

```env
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
LIVEKIT_TRUNK_ID=your_sip_trunk_id
GROQ_API_KEY=your_groq_api_key
```

### Start the Integrated Service

```bash
cd backend
python run_dev.py
```

This single command starts:
- **FastAPI server** at `http://localhost:8000`
- **API documentation** at `http://localhost:8000/docs` 
- **LiveKit agent worker** (integrated within FastAPI)
- **WebSocket endpoints** for real-time updates

## 📡 API Endpoints

### Start a Call
```bash
POST /api/v1/start-call
{
  "phone_number": "+1234567890",
  "system_prompt": "You are a helpful assistant."
}
```

Response includes:
```json
{
  "status": "Call initiated successfully",
  "phone_number": "+1234567890", 
  "call_id": "unique-call-id",
  "websocket_url": "ws://localhost:8000/ws/transcription/unique-call-id"
}
```

### Get Call Status
```bash
GET /api/v1/calls/{call_id}/status
```

### Health Check
```bash
GET /api/v1/health
```

## 🔌 WebSocket Integration

Connect to real-time transcriptions:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/transcription/your-call-id');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'transcription':
      console.log(`${data.speaker}: ${data.text}`);
      break;
    case 'call_status':
      console.log(`Call ${data.status}`);
      break;
    case 'agent_state':
      console.log(`Agent is ${data.state}`);
      break;
  }
};
```

### WebSocket Message Types

1. **Transcription Messages**:
   ```json
   {
     "type": "transcription",
     "call_id": "abc-123",
     "text": "Hello, how can I help you?",
     "speaker": "agent",
     "timestamp": "2024-01-01T12:00:00Z"
   }
   ```

2. **Call Status Updates**:
   ```json
   {
     "type": "call_status", 
     "call_id": "abc-123",
     "status": "connected",
     "data": {"message": "Agent connected and ready"}
   }
   ```

3. **Agent State Changes**:
   ```json
   {
     "type": "agent_state",
     "call_id": "abc-123", 
     "state": "listening"
   }
   ```

## 🧪 Testing

Test the integrated setup:

```bash
# Test API and WebSocket functionality
python test_websocket.py
```

## 🏗️ Architecture

```
FastAPI Application
├── API Endpoints (/api/v1/*)
├── WebSocket Endpoints (/ws/*)
├── LiveKit Worker Manager (integrated)
└── WebSocket Connection Manager
```

### Key Components:

- **`main.py`**: FastAPI app with integrated LiveKit worker
- **`app/services/livekit_worker.py`**: Worker manager using LiveKit's Worker class
- **`app/services/livekit_agent.py`**: Enhanced agent with WebSocket integration  
- **`app/services/websocket_manager.py`**: Manages WebSocket connections
- **`run_dev.py`**: Development runner (single process)

## 🔄 Migration from Separate Process

The old setup required running `worker.py` separately. The new integrated approach:

**Before** (2 processes):
```bash
# Terminal 1
python -m uvicorn main:app --reload

# Terminal 2  
python worker.py
```

**After** (1 process):
```bash
python run_dev.py
```

## 📋 Call Flow

1. **Start Call**: POST to `/start-call` returns `call_id` and WebSocket URL
2. **Connect WebSocket**: Frontend connects to WebSocket for real-time updates
3. **LiveKit Agent**: Processes audio and sends transcriptions via WebSocket
4. **Real-time Updates**: Frontend receives live transcriptions and status updates
5. **Call End**: Final transcript saved to file and sent via WebSocket

## 🔧 Development

For development with hot reload:
```bash
python run_dev.py
```

For production deployment, use a proper ASGI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🚨 Important Notes

- **Single Process**: Everything runs in one FastAPI process now
- **Environment Variables**: Make sure all required env vars are set
- **WebSocket Connections**: Each call gets its own WebSocket channel
- **Error Handling**: Proper cleanup on worker shutdown and WebSocket disconnections
- **Real-time**: Transcriptions are sent immediately, not saved to files first 