import asyncio
import logging
import os
from typing import Optional

from livekit.agents import Worker, WorkerOptions, JobContext, JobRequest
from app.services.livekit_agent import entrypoint
from app.services.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

class LiveKitWorkerManager:
    """Manages the LiveKit Worker directly within the FastAPI application"""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
        self.worker: Optional[Worker] = None
        self._worker_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the LiveKit worker"""
        try:
            # Create worker options
            worker_options = WorkerOptions(
                entrypoint_fnc=self._create_entrypoint_with_websocket,
                request_fnc=self._handle_job_request,
                agent_name="groq-call-agent",
                # Use environment variables for LiveKit connection
                ws_url=os.getenv("LIVEKIT_URL"),
                api_key=os.getenv("LIVEKIT_API_KEY"),
                api_secret=os.getenv("LIVEKIT_API_SECRET"),
            )
            
            # Create and start the worker
            self.worker = Worker(worker_options, devmode=True)
            
            # Start the worker in the background
            self._worker_task = asyncio.create_task(self.worker.run())
            
            logger.info("LiveKit Worker started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start LiveKit Worker: {e}")
            raise
    
    async def stop(self):
        """Stop the LiveKit worker"""
        try:
            if self.worker:
                await self.worker.aclose()
                
            if self._worker_task and not self._worker_task.done():
                self._worker_task.cancel()
                try:
                    await self._worker_task
                except asyncio.CancelledError:
                    pass
                    
            logger.info("LiveKit Worker stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping LiveKit Worker: {e}")
    
    def _create_entrypoint_with_websocket(self, ctx: JobContext):
        """Create an entrypoint function that has access to the WebSocket manager"""
        return entrypoint(ctx, self.websocket_manager)
    
    async def _handle_job_request(self, request: JobRequest):
        """Handle incoming job requests"""
        try:
            logger.info(f"Received job request for room: {request.room.name}")
            
            # Accept all job requests (you can add logic here to filter)
            await request.accept()
            
        except Exception as e:
            logger.error(f"Error handling job request: {e}")
            await request.reject()
    
    @property
    def is_running(self) -> bool:
        """Check if the worker is currently running"""
        return (
            self.worker is not None and 
            self._worker_task is not None and 
            not self._worker_task.done()
        ) 