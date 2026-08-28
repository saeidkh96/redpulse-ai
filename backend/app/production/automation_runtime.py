from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any
from urllib.request import Request, urlopen
import json, time, uuid

class JobStatus(str, Enum): QUEUED="queued"; RUNNING="running"; SUCCEEDED="succeeded"; FAILED="failed"; DEAD="dead"; WAITING_APPROVAL="waiting_approval"
@dataclass(slots=True)
class AutomationJob:
    job_id: str; tenant_id: str; provider: str; event_type: str; payload: dict[str,Any]
    status: JobStatus=JobStatus.QUEUED; attempts: int=0; error: str|None=None
@dataclass(slots=True)
class Approval:
    approval_id: str; tenant_id: str; action: str; approved: bool|None=None; actor: str|None=None

class ApprovalStore:
    def __init__(self): self._items: dict[str,Approval]={}
    def request(self,tenant_id:str,action:str)->Approval:
        a=Approval(str(uuid.uuid4()),tenant_id,action); self._items[a.approval_id]=a; return a
    def decide(self,approval_id:str,approved:bool,actor:str)->Approval:
        a=self._items[approval_id]; a.approved=approved; a.actor=actor; return a
    def get(self,approval_id:str)->Approval: return self._items[approval_id]

class HttpWorkflowExecutor:
    """Runtime used by n8n/Power Automate webhook-style flows when configured."""
    def execute(self,url:str,payload:dict,headers:dict[str,str]|None=None,timeout:float=10.0)->dict:
        req=Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json",**(headers or {})},method="POST")
        with urlopen(req,timeout=timeout) as r: return {"status":r.status,"body":r.read().decode("utf-8","replace")}

class AutomationRuntime:
    def __init__(self,max_attempts:int=3): self.max_attempts=max_attempts; self.jobs={}; self.dead_letter=[]
    def submit(self,tenant_id:str,provider:str,event_type:str,payload:dict)->AutomationJob:
        j=AutomationJob(str(uuid.uuid4()),tenant_id,provider,event_type,payload); self.jobs[j.job_id]=j; return j
    def run(self,job_id:str,handler:Callable[[AutomationJob],Any])->AutomationJob:
        j=self.jobs[job_id]
        while j.attempts < self.max_attempts:
            j.attempts+=1; j.status=JobStatus.RUNNING
            try: handler(j); j.status=JobStatus.SUCCEEDED; j.error=None; return j
            except Exception as e: j.error=str(e); j.status=JobStatus.FAILED
        j.status=JobStatus.DEAD; self.dead_letter.append(j.job_id); return j
