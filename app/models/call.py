from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Call(Base):
    __tablename__ = 'calls'
    
    id = Column(Integer, primary_key=True)
    defaulter_name = Column(String(255))
    phone_number = Column(String(20))
    agent_type = Column(String(100))  # Type of agent/prompt used
    prompt = Column(Text)
    duration = Column(Float)  # Duration in seconds
    outcome = Column(Text)  # Final outcome/summary
    summary = Column(Text)  # AI generated summary
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with call history
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