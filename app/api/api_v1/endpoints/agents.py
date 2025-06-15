from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.base import get_db
from app.models.call import Agent
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class AgentCreate(BaseModel):
    name: str
    prompt: str
    agent_type: str

class AgentUpdate(BaseModel):
    name: str | None = None
    prompt: str | None = None
    agent_type: str | None = None

class AgentResponse(BaseModel):
    id: int
    name: str
    prompt: str
    agent_type: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True

@router.post("/", response_model=AgentResponse)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    db_agent = Agent(
        name=agent.name,
        prompt=agent.prompt,
        agent_type=agent.agent_type
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: int, agent: AgentUpdate, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent.name is not None:
        db_agent.name = agent.name
    if agent.prompt is not None:
        db_agent.prompt = agent.prompt
    if agent.agent_type is not None:
        db_agent.agent_type = agent.agent_type
    
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("/", response_model=List[AgentResponse])
def get_agents(db: Session = Depends(get_db)):
    return db.query(Agent).all()

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent 