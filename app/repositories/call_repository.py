from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from ..models.call import Call, CallHistory

class CallRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_call(self, defaulter_name: str, phone_number: str, agent_type: str, prompt: str) -> Call:
        call = Call(
            defaulter_name=defaulter_name,
            phone_number=phone_number,
            agent_type=agent_type,
            prompt=prompt
        )
        self.db.add(call)
        self.db.commit()
        self.db.refresh(call)
        return call

    def add_call_history(self, call_id: int, role: str, message: str) -> CallHistory:
        history = CallHistory(
            call_id=call_id,
            role=role,
            message=message
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def update_call(self, call_id: int, duration: float, outcome: str, summary: str) -> Optional[Call]:
        call = self.db.query(Call).filter(Call.id == call_id).first()
        if call:
            call.duration = duration
            call.outcome = outcome
            call.summary = summary
            self.db.commit()
            self.db.refresh(call)
        return call

    def get_call(self, call_id: int) -> Optional[Call]:
        return self.db.query(Call).filter(Call.id == call_id).first()

    def get_all_calls(self) -> List[Call]:
        return self.db.query(Call).all()

    def get_call_history(self, call_id: int) -> List[CallHistory]:
        return self.db.query(CallHistory).filter(CallHistory.call_id == call_id).all() 