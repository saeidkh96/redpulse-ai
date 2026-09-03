from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class IndustrialEvent:
    topic:str; key:str; schema_version:int; payload:dict
    occurred_at:datetime=datetime.now(timezone.utc)
    def validate(self)->None:
        if not self.topic or not self.key: raise ValueError("topic and key are required")
        if self.schema_version<1: raise ValueError("schema_version must be >= 1")

class IdempotentConsumer:
    def __init__(self): self._seen:set[str]=set()
    def consume(self,event_id:str,handler, event:IndustrialEvent):
        if event_id in self._seen: return {"duplicate":True}
        event.validate(); value=handler(event); self._seen.add(event_id); return {"duplicate":False,"value":value}
