import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time transcriptions"""
    
    def __init__(self):
        # Store active connections by call_id
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, call_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[call_id] = websocket
        logger.info(f"WebSocket connected for call {call_id}")
        
        # Send initial connection message
        await self.send_to_call(call_id, {
            "type": "connection_established",
            "call_id": call_id,
            "message": "Connected to real-time transcription"
        })
    
    def disconnect(self, call_id: str):
        """Remove a WebSocket connection"""
        if call_id in self.active_connections:
            del self.active_connections[call_id]
            logger.info(f"WebSocket disconnected for call {call_id}")
    
    async def send_to_call(self, call_id: str, data: dict):
        """Send data to a specific call's WebSocket connection"""
        if call_id in self.active_connections:
            try:
                websocket = self.active_connections[call_id]
                await websocket.send_text(json.dumps(data))
            except Exception as e:
                logger.error(f"Error sending to call {call_id}: {e}")
                # Remove broken connection
                self.disconnect(call_id)
    
    async def send_transcription(self, call_id: str, text: str, speaker: str, timestamp: float = None):
        """Send transcription data to the frontend"""
        await self.send_to_call(call_id, {
            "type": "transcription",
            "call_id": call_id,
            "text": text,
            "speaker": speaker,  # 'user' or 'agent'
            "timestamp": timestamp or asyncio.get_event_loop().time()
        })
    
    async def send_call_status(self, call_id: str, status: str, metadata: dict = None):
        """Send call status updates to the frontend"""
        await self.send_to_call(call_id, {
            "type": "call_status",
            "call_id": call_id,
            "status": status,  # 'connecting', 'connected', 'speaking', 'listening', 'ended'
            "metadata": metadata or {}
        })
    
    async def send_agent_state(self, call_id: str, state: str):
        """Send agent state updates (speaking, listening, thinking)"""
        await self.send_to_call(call_id, {
            "type": "agent_state",
            "call_id": call_id,
            "state": state
        })
    
    def get_connected_calls(self) -> Set[str]:
        """Get list of all connected call IDs"""
        return set(self.active_connections.keys())
    
    async def broadcast_to_all(self, data: dict):
        """Send data to all connected clients"""
        for call_id in list(self.active_connections.keys()):
            await self.send_to_call(call_id, data) 