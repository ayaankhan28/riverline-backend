from typing import List
from app.core.config import settings
from google import genai

async def generate_call_summary(messages: List[dict]) -> str:
    """Generate a summary of the call using Groq LLM."""
    
    # Format messages for the LLM
    conversation = "\n".join([
        f"{msg['role'].upper()}: {msg['text']}"
        for msg in messages
    ])
    # Create the prompt
    prompt = f"""You are an expert in analyzing human conversations. Please analyze the following transcript between two individuals and generate a **high-quality, insightful summary** in markdown format. Focus on extracting the **most relevant information**, including tone, intent, emotions, topics discussed, outcomes, and actionable insights.

Please structure your response using the following format:

# 🧾 Summary
A brief overview capturing the essence of the conversation — who is involved, what the context is, and the primary outcome or unresolved point.

## 🧩 Key Topics Discussed
- Bullet points summarizing the main subjects covered
- Any decisions made or proposals offered
- Conflicts, misunderstandings, or breakthroughs

## 🎭 Tone & Sentiment Analysis
- Emotional tone of each speaker (e.g., calm, frustrated, cooperative)
- Overall sentiment of the conversation (positive / negative / neutral)
- Any notable shifts in mood or tension during the conversation

## 🧠 Speaker Intent & Behavior
- Speaker 1: Intent, key motivations, communication style
- Speaker 2: Intent, key motivations, communication style
- Any signs of manipulation, persuasion, empathy, or defensiveness

## ✅ Outcomes & Next Steps
- Agreed actions, follow-ups, or unresolved issues
- Suggestions for how the conversation could proceed or improve in future

---

### 🔍 Transcript:
{conversation}

Please return the analysis in the markdown format as structured above."""

    # Use Groq to generate summary
    # llm = groq.LLM(model="llama3-8b-8192")
    # response = await llm.complete(prompt)
    

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text