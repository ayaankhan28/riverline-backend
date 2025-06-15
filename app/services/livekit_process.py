import os
import json
from datetime import datetime
from dotenv import load_dotenv
import time

from livekit.agents import Agent, AgentSession, JobContext, AutoSubscribe
from livekit.agents.llm.chat_context import ChatContext, ChatMessage
from livekit.plugins import groq, silero, cartesia, sarvam
from livekit import api
import asyncio

from app.models.base import SessionLocal
from app.repositories.call_repository import CallRepository
from app.services.summary_service import generate_call_summary
from app.core.config import settings

load_dotenv()


class VoiceAgent(Agent):
    def __init__(self, prompt: str, room_name: str, defaulter_name: str, phone_number: str, agentId: int):
        super().__init__(instructions=prompt)
        self.dialogue = []
        self.room_name = room_name
        self.start_time = time.time()
        
        # Initialize database
        db = SessionLocal()
        self.call_repo = CallRepository(db)
        
        # Create call record
        self.call = self.call_repo.create_call(
            defaulter_name=defaulter_name,
            phone_number=phone_number,
            agentId=agentId,
        )

    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: ChatMessage) -> None:
        ts = datetime.now().isoformat()
        user_text = new_message.content
        print(f"[USER {ts}] {user_text}")
        self.dialogue.append({"role": "user", "text": user_text, "timestamp": ts})

    async def on_llm_response(self, response_message: ChatMessage) -> None:
        ts = datetime.now().isoformat()
        agent_text = response_message.content
        print(f"[AGENT {ts}] {agent_text}")
        self.dialogue.append({"role": "assistant", "text": agent_text, "timestamp": ts})

    

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    metadata = json.loads(ctx.job.metadata)
    phone = metadata.get("phone_number")
    prompt = metadata.get("system_prompt", "You are a helpful assistant.")
    defaulter_name = metadata.get("defaulter_name", "Unknown")
    agentId = metadata.get("agentId", 1)
    print('Metadata: ', metadata)

    if not phone:
        print("❌ Missing phone number")
        return

    print(f"📞 Calling {phone}...")
    await ctx.api.sip.create_sip_participant(api.CreateSIPParticipantRequest(
        room_name=ctx.room.name,
        sip_trunk_id=os.getenv("LIVEKIT_TRUNK_ID"),
        sip_call_to=phone,
        participant_identity="callee",
        wait_until_answered=True,
    ))

    session = AgentSession(
        stt=groq.STT(model="whisper-large-v3-turbo"),
        llm=groq.LLM(model="llama3-8b-8192"),
        tts=sarvam.TTS(
      target_language_code="hi-IN",
      speaker="manisha",api_key=settings.SARVAM_API_KEY),
        vad=silero.VAD.load(),
        turn_detection="vad",
        allow_interruptions=True,
    )

    agent = VoiceAgent(
        prompt=prompt,
        room_name=ctx.room.name,
        defaulter_name=defaulter_name,
        phone_number=phone,
        agentId=agentId
    )

    @session.on("conversation_item_added")
    def on_conversation_item_added(event):
        if event.item.role == "assistant":
            print(f"[Agent] {event.item.text_content}")
            # Add to call history
            agent.call_repo.add_call_history(
                call_id=agent.call.id,
                role="agent",
                message=event.item.text_content
            )
        else:
            print(f"[User] {event.item.text_content}")
            # Add to call history
            agent.call_repo.add_call_history(
                call_id=agent.call.id,
                role="defaulter",
                message=event.item.text_content
            )
    # Define shutdown hook
    async def shutdown_hook():
        # Get call history from repository
        call_history = agent.call_repo.get_call_history(agent.call.id)
        
        # Format history for summary generation and calculate duration
        messages = []
        first_message_time = None
        last_message_time = None
        
        for history in call_history:
            messages.append({
                'role': history.role,
                'text': history.message
            })
            
            if first_message_time is None:
                first_message_time = history.created_at
            last_message_time = history.created_at
        
        # Calculate duration in minutes
        if first_message_time and last_message_time:
            duration = (last_message_time - first_message_time).total_seconds() / 60
        else:
            duration = 0
        
        # Generate summary
        summary = await generate_call_summary(messages)
        
        # Update call with summary and duration
        agent.call_repo.update_call(
            call_id=agent.call.id,
            duration=duration,
            outcome="Completed", 
            summary=summary
        )
        
        print("Call ended and summary generated")

    # Add shutdown hook
    ctx.add_shutdown_callback(shutdown_hook)
    await session.start(agent=agent, room=ctx.room)

    