
import os
import json
from datetime import datetime
from dotenv import load_dotenv

from livekit.agents import Agent, AgentSession, JobContext, AutoSubscribe
from livekit.agents.llm.chat_context import ChatContext, ChatMessage
from livekit.plugins import groq, silero, cartesia
from livekit import api

load_dotenv()

class VoiceAgent(Agent):
    def __init__(self, prompt: str):
        super().__init__(instructions=prompt)
        self.dialogue = []

    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: ChatMessage) -> None:
        ts = datetime.now().isoformat()
        print("TESTING",new_message)
        user_text = new_message.content
        print(f"[USER {ts}] {user_text}")
        self.dialogue.append({"role": "user", "text": user_text, "timestamp": ts})

    async def on_llm_response(self, response_message: ChatMessage) -> None:
        ts = datetime.now().isoformat()
        print("TESTING",response_message)
        agent_text = response_message.content
        print(f"[AGENT {ts}] {agent_text}")
        self.dialogue.append({"role": "assistant", "text": agent_text, "timestamp": ts})

    async def on_session_end(self, session):
        with open("call_transcript.json", "w") as f:
            json.dump(self.dialogue, f, indent=2)
        print("✅ Transcript saved to call_transcript.json")

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    metadata = json.loads(ctx.job.metadata)
    phone = metadata.get("phone_number")
    prompt = metadata.get("system_prompt", "You are a helpful assistant.")

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
        tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
        vad=silero.VAD.load(),
        turn_detection="vad",
        allow_interruptions=True,
    )


    @session.on("conversation_item_added")
    def on_conversation_item_added(event):
        if event.item.role == "assistant":
            print(f"[Agent] {event.item.text_content}")
        else:
            print(f"[User] {event.item.text_content}")
    await session.start(agent=VoiceAgent(prompt=prompt), room=ctx.room)

