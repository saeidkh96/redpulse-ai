from fastapi import APIRouter
from app.schemas.v32_platform import LakehouseProcessRequest,GovernanceGrantRequest,DigitalPlatformReadinessRequest,OperationalValidationRequest
from app.services.v32_platform import v32_platform_service
router=APIRouter(prefix='/api/v1/v32-platform',tags=['v3.2-v4.0 Platform'])
@router.post('/lakehouse/process')
def process_lakehouse(body:LakehouseProcessRequest): return v32_platform_service.process_telemetry(body.model_dump())
@router.post('/governance/grants')
def create_grant(body:GovernanceGrantRequest):
 g=v32_platform_service.governance.grant(body.principal,body.securable,body.privileges); return {'principal':g.principal,'securable':g.securable,'privileges':list(g.privileges)}
@router.post('/hardening/readiness')
def readiness(body:DigitalPlatformReadinessRequest): return v32_platform_service.readiness(body.availability,body.p95_latency_ms)
@router.post('/operational-validation')
def operational(body:OperationalValidationRequest): return v32_platform_service.operational_validation(**body.model_dump())
