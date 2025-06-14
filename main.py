from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from typing import Dict, Set

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.services.livekit_worker import LiveKitWorkerManager
from app.services.websocket_manager import WebSocketManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global managers
websocket_manager = WebSocketManager()
livekit_worker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - starts and stops the LiveKit worker"""
    global livekit_worker
    
    logger.info("🚀 Starting LiveKit Worker within FastAPI...")
    
    # Initialize and start the LiveKit worker
    livekit_worker = LiveKitWorkerManager(websocket_manager)
    await livekit_worker.start()
    
    logger.info("✅ LiveKit Worker started successfully")
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 Stopping LiveKit Worker...")
    if livekit_worker:
        await livekit_worker.stop()
    logger.info("✅ LiveKit Worker stopped")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint for real-time transcriptions
@app.websocket("/ws/transcription/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    await websocket_manager.connect(websocket, call_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Handle any client messages if needed
            logger.info(f"Received message from client {call_id}: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(call_id)
        logger.info(f"Client {call_id} disconnected")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

