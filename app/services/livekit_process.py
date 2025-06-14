# agent_worker.py
import os, json
from livekit.agents import Agent, AgentSession, JobContext
from livekit.plugins import groq, silero
from livekit import api
from dotenv import load_dotenv

load_dotenv()
    
class VoiceAgent(Agent):
    def __init__(self, prompt: str):
        super().__init__(instructions=prompt)
        self.dialogue = []

    async def intercept(self, text, stage):
        print(f"[{stage.upper()}] {text}")
        self.dialogue.append({"role": stage, "text": text})
        return text

    async def on_session_end(self, session):
        with open("call_transcript.json", "w") as f:
            json.dump(self.dialogue, f, indent=2)
        print("✅ Transcript saved")

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    metadata = json.loads(ctx.job.metadata)
    phone = metadata.get("phone_number")
    prompt = metadata.get("system_prompt", "You are a helpful assistant.")

    if not phone:
        print("❌ Missing phone number")
        return

    print(f"📞 Calling {phone}...")
    await ctx.api.sip.create_sip_participant(
        api.CreateSIPParticipantRequest(
            room_name=ctx.room.name,
            sip_trunk_id=os.getenv("LIVEKIT_TRUNK_ID"),
            sip_call_to=phone,
            participant_identity="callee",
            wait_until_answered=True,
        )
    )

    session = AgentSession(
        stt=groq.STT(model="whisper-large-v3-turbo"),
        llm=groq.LLM(model="llama3-8b-8192"),
        tts=groq.TTS(model="playai-tts", voice="Arista-PlayAI"),
        vad=silero.VAD.load(),
        turn_detection="vad",
        allow_interruptions=True,
    )
    await session.start(agent=VoiceAgent(prompt=prompt), room=ctx.room)
