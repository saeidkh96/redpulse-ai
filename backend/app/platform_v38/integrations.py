from dataclasses import dataclass
from enum import Enum

class Adapter(str,Enum): N8N="n8n"; POWER_AUTOMATE="power_automate"; WEBHOOK="webhook"
@dataclass(frozen=True)
class IntegrationMessage:
    event_type:str; tenant_id:str; idempotency_key:str; payload:dict
class IntegrationGateway:
    def __init__(self): self.adapters={}
    def register(self,name:Adapter,send): self.adapters[name]=send
    def dispatch(self,name:Adapter,msg:IntegrationMessage):
        if not msg.idempotency_key: raise ValueError("idempotency_key required")
        if name not in self.adapters: raise KeyError(name)
        return self.adapters[name](msg)
