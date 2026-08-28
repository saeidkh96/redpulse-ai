from pathlib import Path
from app.runtime_v3.persistence import JsonRuntimeRepository
from app.runtime_v3.engine import PersistentJobRuntime
from app.services.production_demo_v3 import ProductionDemoService

def test_demo_service(tmp_path: Path):
    svc = ProductionDemoService(PersistentJobRuntime(JsonRuntimeRepository(tmp_path/"r.json")))
    out = svc.run("t1","m1",{"health_score":0.3,"deviation_score":0.8,"drift_score":0.7})
    assert out["machine_id"] == "m1"
    assert out["requires_approval"] is True
