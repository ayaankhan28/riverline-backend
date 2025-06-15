from fastapi import APIRouter
from app.api.api_v1.endpoints import users, websocket, calls, agents

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"]) 
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])