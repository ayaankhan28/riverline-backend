import uuid
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from livekit import api
from app.core.config import settings

router = APIRouter()

class CallRequest(BaseModel):
    phone_number: str
    system_prompt: str

class CallResponse(BaseModel):
    status: str
    phone_number: str
    call_id: str
    websocket_url: str

@router.post("/start-call", response_model=CallResponse)
async def start_call(req: CallRequest):
    """Start a new voice agent call with WebSocket support"""
    
    # Generate unique call ID for tracking
    call_id = str(uuid.uuid4())
    
    try:
        lkapi = api.LiveKitAPI(
            url=settings.LIVEKIT_URL,
            api_key=settings.LIVEKIT_API_KEY,
            api_secret=settings.LIVEKIT_API_SECRET
        )

        # Create dispatch with call_id in metadata
        await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name="groq-call-agent",
                room="my_room",  # auto-generate
                metadata=json.dumps({
                    "phone_number": req.phone_number,
                    "system_prompt": req.system_prompt,
                    "call_id": call_id
                })
            )
        )

        await lkapi.aclose()
        
        # Return response with WebSocket URL for real-time updates
        return CallResponse(
            status="Call initiated successfully",
            phone_number=req.phone_number,
            call_id=call_id,
            websocket_url=f"ws://localhost:8000/ws/transcription/{call_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start call: {str(e)}"
        )

@router.get("/calls/{call_id}/status")
async def get_call_status(call_id: str):
    """Get the current status of a call"""
    # In a real implementation, you might store call status in a database
    # For now, return basic info
    return {
        "call_id": call_id,
        "status": "active",  # This would be fetched from actual call state
        "websocket_url": f"ws://localhost:8000/ws/transcription/{call_id}"
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "voice-agent-backend",
        "livekit_integration": "embedded"
    }
