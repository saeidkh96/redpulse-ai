from dataclasses import dataclass,field
import time

@dataclass
class RuntimeMetrics:
    retries:int=0; takeovers:int=0; dead_letters:int=0; recoveries:list[float]=field(default_factory=list)
    def recovery(self,seconds:float): self.recoveries.append(seconds)
    @property
    def mean_recovery_seconds(self): return sum(self.recoveries)/len(self.recoveries) if self.recoveries else 0.0
@dataclass(frozen=True)
class SLO:
    availability:float=.995; p95_latency_ms:float=750
    def evaluate(self,availability:float,p95_latency_ms:float): return {"availability_ok":availability>=self.availability,"latency_ok":p95_latency_ms<=self.p95_latency_ms}
