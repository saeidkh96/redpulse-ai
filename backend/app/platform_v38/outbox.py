from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

@dataclass
class OutboxEvent:
    topic:str; key:str; payload:dict
    id:str=field(default_factory=lambda:str(uuid4()))
    created_at:datetime=field(default_factory=lambda:datetime.now(timezone.utc))
    delivered:bool=False

class TransactionalOutbox:
    """Storage-agnostic outbox contract; persistence adapter can replace this test implementation."""
    def __init__(self): self._events:dict[str,OutboxEvent]={}
    def add(self,topic:str,key:str,payload:dict)->OutboxEvent:
        event=OutboxEvent(topic,key,payload); self._events[event.id]=event; return event
    def pending(self)->list[OutboxEvent]: return [e for e in self._events.values() if not e.delivered]
    def mark_delivered(self,event_id:str)->None: self._events[event_id].delivered=True
