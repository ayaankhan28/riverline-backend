#!/usr/bin/env python3
"""
Development runner script
This script runs the FastAPI server with integrated LiveKit worker.
Run this script with: python run_dev.py
"""

import subprocess
import sys
import signal
import os

def signal_handler(sig, frame):
    print("\n🛑 Received interrupt signal. Shutting down...")
    sys.exit(0)

def run_fastapi():
    """Run the FastAPI server with integrated LiveKit worker"""
    print("🚀 Starting FastAPI server with integrated LiveKit worker...")
    
    # Check for required environment variables
    required_vars = [
        "LIVEKIT_URL", 
        "LIVEKIT_API_KEY", 
        "LIVEKIT_API_SECRET", 
        "GROQ_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return
    
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--port", "8000", 
        "--reload"
    ])

if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🔥 Starting development environment...")
    print("📡 FastAPI will be available at: http://localhost:8000")
    print("📄 API docs will be available at: http://localhost:8000/docs")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws/transcription/{call_id}")
    print("🤖 LiveKit worker is integrated within FastAPI")
    print("Press Ctrl+C to stop the service\n")
    
    try:
        run_fastapi()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error starting development environment: {e}") 