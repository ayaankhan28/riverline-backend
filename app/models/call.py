from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Agent(Base):
    __tablename__ = 'agents'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    agent_type = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with calls
    calls = relationship("Call", back_populates="agent")

class Call(Base):
    __tablename__ = 'calls'
    
    id = Column(Integer, primary_key=True)
    defaulter_name = Column(String(255))
    phone_number = Column(String(20))
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=False)
    duration = Column(Float)  # Duration in seconds
    outcome = Column(Text)  # Final outcome/summary
    summary = Column(Text)  # AI generated summary
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="calls")
    history = relationship("CallHistory", back_populates="call")

class CallHistory(Base):
    __tablename__ = 'call_history'
    
    id = Column(Integer, primary_key=True)
    call_id = Column(Integer, ForeignKey('calls.id'))
    role = Column(String(50))  # 'defaulter' or 'agent'
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with call
    call = relationship("Call", back_populates="history") 