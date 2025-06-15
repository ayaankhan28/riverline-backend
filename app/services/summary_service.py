from typing import List
from livekit.plugins import groq

async def generate_call_summary(messages: List[dict]) -> str:
    """Generate a summary of the call using Groq LLM."""
    
    # Format messages for the LLM
    conversation = "\n".join([
        f"{msg['role'].upper()}: {msg['text']}"
        for msg in messages
    ])
    
    # Create the prompt
    prompt = f"""Please analyze this conversation between a debt collection agent and a defaulter, and provide a concise summary including:
1. Key points discussed
2. Defaulter's response/attitude
3. Any agreements or promises made
4. Next steps or follow-up actions

Conversation:
{conversation}

Summary:"""

    # Use Groq to generate summary
    # llm = groq.LLM(model="llama3-8b-8192")
    # response = await llm.complete(prompt)
    Mock_summary = """
    The defaulter was very rude and refused to pay the debt.
    The agent was able to get the defaulter to agree to pay a portion of the debt.
    The defaulter was very rude and refused to pay the debt.
    """
    return Mock_summary