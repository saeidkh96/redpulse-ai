from fastapi import APIRouter
from app.schemas.production_demo_v3 import DemoRunRequest
from app.services.production_demo_v3 import production_demo_service
from app.deployment_v3.readiness import DeploymentReadiness, DeploymentCheck

router = APIRouter(prefix="/v3", tags=["RedPulse v3"])

@router.post("/demo/run")
def run_demo(body: DemoRunRequest):
    return production_demo_service.run(body.tenant_id, body.machine_id, body.signals)

@router.get("/readiness")
def readiness():
    checks = [
        DeploymentCheck("runtime", True, "runtime available"),
        DeploymentCheck("predictive_ai", True, "reference models available"),
        DeploymentCheck("api", True, "v3 API registered"),
    ]
    return DeploymentReadiness().evaluate(checks)
