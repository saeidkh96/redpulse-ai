from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import uuid
@dataclass(frozen=True,slots=True)
class DecisionRecord:
    decision_id:str; tenant_id:str; actor:str; action:str; entity_id:str; evidence:dict; outcome:str; created_at:str
class DecisionTrail:
    def __init__(self): self._records=[]
    def record(self,tenant_id,actor,action,entity_id,evidence,outcome):
        r=DecisionRecord(str(uuid.uuid4()),tenant_id,actor,action,entity_id,evidence,outcome,datetime.now(timezone.utc).isoformat()); self._records.append(r); return r
    def list(self,tenant_id:str): return [asdict(r) for r in self._records if r.tenant_id==tenant_id]
