from app.production.control_plane import ProductionControlPlane
from app.production.predictive_ai import DriftSignal, RetrainingPolicy
from app.production.data_platform import DataQuality, partition_fleet
class ProductionPlatformService:
    def __init__(self): self.platform=ProductionControlPlane(); self.retraining=RetrainingPolicy()
    def readiness(self):
        r=self.platform.readiness(); return {"version":r.version,"ready":r.ready,"checks":[{"name":c.name,"ok":c.ok,"detail":c.detail} for c in r.checks],"generated_at":r.generated_at}
    def drift(self,model,score,threshold): return {"retrain":self.retraining.should_retrain(DriftSignal(model,score,threshold))}
    def quality(self,record,required): return DataQuality.check(record,set(required))
    def partitions(self,machines,partitions): return [{"partition_id":p.partition_id,"machine_ids":list(p.machine_ids)} for p in partition_fleet(machines,partitions)]
production_platform_service=ProductionPlatformService()
