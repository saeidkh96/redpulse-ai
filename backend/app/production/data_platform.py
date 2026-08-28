from dataclasses import dataclass, field
from typing import Any
import hashlib, json
@dataclass(frozen=True,slots=True)
class EventPolicy: max_retries:int=3; dlq_topic:str="redpulse.dlq"; replay_enabled:bool=True
@dataclass(frozen=True,slots=True)
class SparkJobSpec: name:str; entrypoint:str; partitions:int=8
@dataclass(frozen=True,slots=True)
class TelemetryPoint: machine_id:str; ts:str; metrics:dict[str,float]
class TelemetryRepository:
    """Contract boundary for TimescaleDB or another time-series implementation."""
    def write(self,point:TelemetryPoint)->None: raise NotImplementedError
    def query(self,machine_id:str,start:str,end:str)->list[TelemetryPoint]: raise NotImplementedError
@dataclass(frozen=True,slots=True)
class DatasetRef: dataset_id:str; uri:str; schema_version:str
class DatasetCatalog:
    def __init__(self): self._items={}
    def register(self,ref:DatasetRef): self._items[ref.dataset_id]=ref
    def get(self,dataset_id:str)->DatasetRef: return self._items[dataset_id]
class DataQuality:
    @staticmethod
    def check(record:dict,required:set[str])->dict:
        missing=sorted(required-set(record)); return {"ok":not missing,"missing":missing}
@dataclass(frozen=True,slots=True)
class LineageRecord: dataset_id:str; feature_version:str; model_version:str; prediction_id:str
class LineageStore:
    def __init__(self): self.records=[]
    def add(self,r:LineageRecord): self.records.append(r)
@dataclass(frozen=True,slots=True)
class ReplayPlan: source:str; start:str; end:str; target_topic:str
@dataclass(frozen=True,slots=True)
class WorkPartition: partition_id:int; machine_ids:tuple[str,...]
def partition_fleet(machine_ids:list[str],partitions:int)->list[WorkPartition]:
    buckets=[[] for _ in range(max(1,partitions))]
    for m in sorted(machine_ids): buckets[int(hashlib.sha256(m.encode()).hexdigest(),16)%len(buckets)].append(m)
    return [WorkPartition(i,tuple(v)) for i,v in enumerate(buckets)]
