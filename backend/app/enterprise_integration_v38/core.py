from dataclasses import dataclass
from enum import Enum
import json
from urllib import request
class Provider(str,Enum): N8N='n8n'; POWER_AUTOMATE='power_automate'; WEBHOOK='webhook'
@dataclass(frozen=True)
class IntegrationEndpoint: provider:Provider; url:str; timeout_seconds:float=10.0
class IntegrationRouter:
 def build_request(self,e,event_type,payload): return request.Request(e.url,data=json.dumps({'event_type':event_type,'payload':payload}).encode(),headers={'Content-Type':'application/json'},method='POST')
 def dispatch(self,e,event_type,payload):
  with request.urlopen(self.build_request(e,event_type,payload),timeout=e.timeout_seconds) as r: return {'status':r.status,'body':r.read().decode()}
