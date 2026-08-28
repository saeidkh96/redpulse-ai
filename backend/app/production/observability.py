from dataclasses import dataclass
from collections import defaultdict, deque
import time
@dataclass(frozen=True,slots=True)
class SLO: name:str; target:float; window:str="30d"
class MetricsRegistry:
    def __init__(self): self.counters=defaultdict(float)
    def inc(self,name:str,value:float=1.0): self.counters[name]+=value
class TraceBuffer:
    def __init__(self,maxlen=1000): self.items=deque(maxlen=maxlen)
    def add(self,trace_id:str,span:str,duration_ms:float): self.items.append({"trace_id":trace_id,"span":span,"duration_ms":duration_ms})
class RateLimiter:
    def __init__(self,limit:int,window_seconds:float=60): self.limit=limit; self.window=window_seconds; self.hits=defaultdict(deque)
    def allow(self,key:str)->bool:
        now=time.time(); q=self.hits[key]
        while q and q[0] <= now-self.window: q.popleft()
        if len(q)>=self.limit: return False
        q.append(now); return True
class CircuitBreaker:
    def __init__(self,threshold:int=5): self.threshold=threshold; self.failures=0; self.open=False
    def success(self): self.failures=0; self.open=False
    def failure(self): self.failures+=1; self.open=self.failures>=self.threshold
    def allow(self): return not self.open
