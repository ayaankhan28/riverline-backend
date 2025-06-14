import os
import json
import asyncio
import logging
from typing import Optional

from livekit.agents import Agent, AgentSession, JobContext
from livekit.plugins import groq, silero
from livekit import api
from dotenv import load_dotenv

from app.services.websocket_manager import WebSocketManager

load_dotenv()
logger = logging.getLogger(__name__)

class VoiceAgent(Agent):
    """Enhanced Voice Agent with WebSocket integration for real-time transcriptions"""
    
    def __init__(self, prompt: str, websocket_manager: WebSocketManager, call_id: str):
        super().__init__(instructions=prompt)
        self.dialogue = []
        self.websocket_manager = websocket_manager
        self.call_id = call_id
        
    async def on_enter(self):
        """Called when the agent enters the session"""
        logger.info(f"Voice agent entered session for call {self.call_id}")
        await self.websocket_manager.send_call_status(
            self.call_id, 
            "connected", 
            {"message": "Agent connected and ready"}
        )
    
    async def on_exit(self):
        """Called when the agent exits the session"""
        logger.info(f"Voice agent exited session for call {self.call_id}")
        await self.websocket_manager.send_call_status(
            self.call_id, 
            "ended", 
            {"message": "Call ended"}
        )
    
    async def intercept_text(self, text: str, stage: str):
        """Intercept and process text at different stages"""
        logger.info(f"[{stage.upper()}] {text}")
        
        # Store in dialogue history
        self.dialogue.append({"role": stage, "text": text, "timestamp": asyncio.get_event_loop().time()})
        
        # Send real-time transcription to WebSocket
        speaker = "agent" if stage in ["tts", "llm_response"] else "user"
        await self.websocket_manager.send_transcription(
            self.call_id,
            text,
            speaker
        )
        
        return text
    
    async def on_user_speech_committed(self, message):
        """Called when user finishes speaking"""
        logger.info(f"User speech committed: {message.content}")
        await self.websocket_manager.send_agent_state(self.call_id, "thinking")
        
    async def on_agent_speech_started(self):
        """Called when agent starts speaking"""
        logger.info("Agent started speaking")
        await self.websocket_manager.send_agent_state(self.call_id, "speaking")
        
    async def on_agent_speech_ended(self):
        """Called when agent stops speaking"""
        logger.info("Agent stopped speaking")
        await self.websocket_manager.send_agent_state(self.call_id, "listening")
    
    async def on_session_end(self, session):
        """Called when the session ends"""
        # Save transcript to file
        transcript_file = f"call_transcript_{self.call_id}.json"
        with open(transcript_file, "w") as f:
            json.dump(self.dialogue, f, indent=2)
        
        logger.info(f"✅ Transcript saved to {transcript_file}")
        
        # Send final transcript via WebSocket
        await self.websocket_manager.send_to_call(self.call_id, {
            "type": "transcript_complete",
            "call_id": self.call_id,
            "transcript": self.dialogue,
            "file_path": transcript_file
        })

async def entrypoint(ctx: JobContext, websocket_manager: WebSocketManager):
    """Enhanced entrypoint with WebSocket integration"""
    await ctx.connect()
    
    # Extract metadata
    metadata = json.loads(ctx.job.metadata) if ctx.job.metadata else {}
    phone = metadata.get("phone_number")
    prompt = metadata.get("system_prompt", "You are a helpful assistant.")
    call_id = metadata.get("call_id", ctx.job.id)
    
    if not phone:
        logger.error("❌ Missing phone number")
        await websocket_manager.send_call_status(
            call_id, 
            "error", 
            {"message": "Missing phone number"}
        )
        return

    logger.info(f"📞 Calling {phone}...")
    
    try:
        # Update call status
        await websocket_manager.send_call_status(
            call_id, 
            "connecting", 
            {"phone_number": phone}
        )
        
        # Initiate SIP call
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=os.getenv("LIVEKIT_TRUNK_ID"),
                sip_call_to=phone,
                participant_identity="callee",
                wait_until_answered=True,
            )
        )
        
        # Create enhanced agent session with WebSocket integration
        session = AgentSession(
            stt=groq.STT(model="whisper-large-v3-turbo"),
            llm=groq.LLM(model="llama3-8b-8192"),
            tts=groq.TTS(model="playai-tts", voice="Arista-PlayAI"),
            vad=silero.VAD.load(),
            turn_detection="vad",
            allow_interruptions=True,
        )
        
        # Set up session event handlers for WebSocket integration
        @session.on("user_speech_started")
        async def on_user_speech_started():
            await websocket_manager.send_agent_state(call_id, "listening")
            
        @session.on("user_speech_ended") 
        async def on_user_speech_ended():
            await websocket_manager.send_agent_state(call_id, "thinking")
            
        @session.on("agent_speech_started")
        async def on_agent_speech_started():
            await websocket_manager.send_agent_state(call_id, "speaking")
            
        @session.on("agent_speech_ended")
        async def on_agent_speech_ended():
            await websocket_manager.send_agent_state(call_id, "listening")
        
        # Start the agent session
        agent = VoiceAgent(prompt=prompt, websocket_manager=websocket_manager, call_id=call_id)
        await session.start(agent=agent, room=ctx.room)
        
    except Exception as e:
        logger.error(f"Error in call session: {e}")
        await websocket_manager.send_call_status(
            call_id, 
            "error", 
            {"message": str(e)}
        ) 