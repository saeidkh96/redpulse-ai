from pydantic import BaseModel, Field
class ApprovalRequest(BaseModel): tenant_id:str; action:str
class ApprovalDecisionRequest(BaseModel): approved:bool; actor:str
class JobSubmitRequest(BaseModel): tenant_id:str; provider:str; event_type:str; payload:dict=Field(default_factory=dict)
class DriftRequest(BaseModel): model:str; score:float; threshold:float
class QualityRequest(BaseModel): record:dict; required:list[str]
class FleetPartitionRequest(BaseModel): machine_ids:list[str]; partitions:int=Field(default=8,ge=1,le=1024)
