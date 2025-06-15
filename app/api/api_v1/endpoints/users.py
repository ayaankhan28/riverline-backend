from fastapi import APIRouter
from pydantic import BaseModel
from livekit import api
from app.core.config import settings
import json
import uuid

router = APIRouter()

class CallRequest(BaseModel):
    phone_number: str
    system_prompt: str

@router.post("/start-call")
async def start_call(req: CallRequest):
    # Generate a unique room name
    room_name = f"call-{uuid.uuid4()}"

    lkapi = api.LiveKitAPI(
        url=settings.LIVEKIT_URL,
        api_key=settings.LIVEKIT_API_KEY,
        api_secret=settings.LIVEKIT_API_SECRET
    )

    await lkapi.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name="groq-call-agent",
            room=room_name,
            metadata=json.dumps({
                "phone_number": req.phone_number,
                "system_prompt": req.system_prompt
            })
        )
    )

    await lkapi.aclose()
    return {
        "status": "Call started", 
        "phone_number": req.phone_number,
        "room_name": room_name
    }
