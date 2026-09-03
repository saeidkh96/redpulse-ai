from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import random
import time
from typing import Callable, TypeVar

T=TypeVar("T")
class FailureClass(str, Enum):
    TRANSIENT="transient"
    PERMANENT="permanent"

@dataclass(frozen=True)
class RetryPolicy:
    max_attempts:int=4
    base_delay_seconds:float=0.05
    max_delay_seconds:float=2.0
    jitter_ratio:float=0.2
    def delay(self, attempt:int, rng:Callable[[],float]=random.random)->float:
        raw=min(self.max_delay_seconds,self.base_delay_seconds*(2**max(0,attempt-1)))
        return max(0.0,raw*(1+self.jitter_ratio*((rng()*2)-1)))

@dataclass
class DeadLetter:
    key:str; reason:str; attempts:int; payload:dict

@dataclass
class DeadLetterQueue:
    records:list[DeadLetter]=field(default_factory=list)
    def put(self, record:DeadLetter)->None: self.records.append(record)

class FailureEngine:
    def __init__(self, policy:RetryPolicy|None=None, dlq:DeadLetterQueue|None=None):
        self.policy=policy or RetryPolicy(); self.dlq=dlq or DeadLetterQueue()
    def execute(self,key:str,payload:dict,operation:Callable[[],T],classify:Callable[[Exception],FailureClass])->T:
        for attempt in range(1,self.policy.max_attempts+1):
            try: return operation()
            except Exception as exc:
                kind=classify(exc)
                if kind is FailureClass.PERMANENT or attempt==self.policy.max_attempts:
                    self.dlq.put(DeadLetter(key,str(exc),attempt,payload)); raise
                time.sleep(self.policy.delay(attempt))
        raise RuntimeError("unreachable")
