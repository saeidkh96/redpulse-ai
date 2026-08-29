from dataclasses import dataclass
from typing import Any,Callable
import hashlib
@dataclass(frozen=True)
class EventEnvelope: topic:str; key:str; payload:dict[str,Any]
@dataclass(frozen=True)
class SparkWorkloadSpec: name:str; input_table:str; output_table:str; partitions:int=8
class FleetPartitionPlanner:
 @staticmethod
 def partition(machine_ids,partitions):
  if partitions<=0: raise ValueError("partitions must be > 0")
  out={i:[] for i in range(partitions)}
  for m in machine_ids: out[int(hashlib.sha256(m.encode()).hexdigest(),16)%partitions].append(m)
  return out
class MicroBatchProcessor:
 def __init__(self,batch_size=100): self.batch_size=batch_size
 def run(self,events,handler): return [handler(events[i:i+self.batch_size]) for i in range(0,len(events),self.batch_size)]
