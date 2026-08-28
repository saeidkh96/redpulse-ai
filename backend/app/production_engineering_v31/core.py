from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict
import json

@dataclass(slots=True)
class PersistentRecord:
    record_id: str
    tenant_id: str
    record_type: str
    payload: dict

class DurableJsonStore:
    """Restart-safe local reference store; production can swap PostgreSQL repositories."""
    def __init__(self, path: str | Path = 'artifacts/v31/store.json') -> None:
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self.path.write_text('{}', encoding='utf-8')
    def _read(self): return json.loads(self.path.read_text(encoding='utf-8') or '{}')
    def upsert(self, record: PersistentRecord):
        data=self._read(); data[record.record_id]=asdict(record); self.path.write_text(json.dumps(data,indent=2),encoding='utf-8'); return record
    def get(self, record_id: str): return PersistentRecord(**self._read()[record_id])

@dataclass(frozen=True)
class StreamMessage:
    topic: str
    key: str
    payload: dict
    schema_version: str='1'

class DeadLetterQueue:
    def __init__(self): self.messages=[]
    def push(self,message,error): self.messages.append({'message':message,'error':error})

class ConsumerRuntime:
    def __init__(self,max_attempts:int=3,dlq:DeadLetterQueue|None=None): self.max_attempts=max_attempts; self.dlq=dlq or DeadLetterQueue()
    def process(self,message,handler):
        err=None
        for attempt in range(1,self.max_attempts+1):
            try: return {'status':'processed','attempts':attempt,'result':handler(message)}
            except Exception as exc: err=str(exc)
        self.dlq.push(message,err or 'unknown'); return {'status':'dead_lettered','attempts':self.max_attempts,'error':err}

class MetricStore:
    def __init__(self): self.counters=defaultdict(int); self.gauges={}
    def inc(self,name,value=1): self.counters[name]+=value
    def gauge(self,name,value): self.gauges[name]=float(value)
    def snapshot(self): return {'counters':dict(self.counters),'gauges':dict(self.gauges)}

class ReleaseGate:
    REQUIRED=('compile','tests','lint','security','docker_build')
    def evaluate(self,results:dict[str,bool]):
        failed=[x for x in self.REQUIRED if not results.get(x,False)]
        return {'release_ready':not failed,'failed':failed}
