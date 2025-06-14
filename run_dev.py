#!/usr/bin/env python3
"""
Development runner script
This script runs both the FastAPI server and the LiveKit worker in parallel.
Run this script with: python run_dev.py
"""

import subprocess
import sys
import signal
import time
from threading import Thread

def run_fastapi():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--port", "8000", 
        "--reload"
    ])

def run_worker():
    """Run the LiveKit worker"""
    print("🤖 Starting LiveKit worker...")
    # Give FastAPI a moment to start first
    time.sleep(2)
    subprocess.run([sys.executable, "worker.py","dev"])

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down...")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🔥 Starting development environment...")
    print("📡 FastAPI will be available at: http://localhost:8000")
    print("📄 API docs will be available at: http://localhost:8000/docs")
    print("🤖 LiveKit worker will connect to your LiveKit server")
    print("Press Ctrl+C to stop all services\n")
    
    # Start both services in separate threads
    fastapi_thread = Thread(target=run_fastapi, daemon=True)
    worker_thread = Thread(target=run_worker, daemon=True)
    
    fastapi_thread.start()
    worker_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n�� Shutting down...") 