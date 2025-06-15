from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.models.base import get_db
from app.repositories.call_repository import CallRepository

router = APIRouter()

class CallHistoryResponse(BaseModel):
    id: int
    role: str
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class CallResponse(BaseModel):
    id: int
    defaulter_name: str
    phone_number: str
    agent_type: str
    duration: float | None
    outcome: str | None
    summary: str | None
    created_at: datetime
    history: List[CallHistoryResponse] | None
    
    class Config:
        from_attributes = True

@router.get("/calls/", response_model=List[CallResponse])
def get_all_calls(db: Session = Depends(get_db)):
    """Get all calls with their summaries."""
    repo = CallRepository(db)
    calls = repo.get_all_calls()
    return calls

@router.get("/calls/{call_id}", response_model=CallResponse)
def get_call_details(call_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific call including its history."""
    repo = CallRepository(db)
    call = repo.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # Get call history
    call.history = repo.get_call_history(call_id)
    return call 