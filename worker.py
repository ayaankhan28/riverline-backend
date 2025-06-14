#!/usr/bin/env python3
"""
LiveKit Agent Worker
This script runs the LiveKit agent worker separately from the FastAPI application.
Run this script with: python worker.py
"""

from app.services.livekit_process import entrypoint
from livekit.agents import cli, WorkerOptions

if __name__ == "__main__":
    # Run the LiveKit agent worker
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint, 
        agent_name="groq-call-agent"
    )) 