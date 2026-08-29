from app.lakehouse_v32.core import MedallionPipeline
from app.governance_v33.unity_catalog import UnityCatalogGovernance
from app.platform_hardening_v39.core import PlatformHardening,SLO
from app.operational_validation_v40.core import OperationalEvidence,OperationalValidator
class V32PlatformService:
 def __init__(self): self.medallion=MedallionPipeline(); self.governance=UnityCatalogGovernance(); self.hardening=PlatformHardening(); self.operational=OperationalValidator()
 def process_telemetry(self,payload):
  r=self.medallion.process(payload); return {k:{'record_id':v.record_id,'layer':v.layer.value,'payload':v.payload,'quality':v.quality} for k,v in r.items()}
 def readiness(self,a,p): return self.hardening.evaluate_slo(a,p,SLO())
 def operational_validation(self,**kw): return self.operational.evaluate(OperationalEvidence(**kw))
v32_platform_service=V32PlatformService()
