from fastapi import APIRouter,HTTPException
from dataclasses import asdict
from app.schemas.v31_platform import TwinCreateRequest,TwinScenarioRequest,FusionRequest,RULRequest
from app.services.v31_platform import v31_platform_service as service
router=APIRouter(prefix='/v3.1',tags=['RedPulse v3.1'])
@router.get('/readiness')
def readiness(): return service.readiness()
@router.post('/digital-twins')
def create_twin(body:TwinCreateRequest): return service.create_twin(body)
@router.post('/digital-twins/simulate')
def simulate(body:TwinScenarioRequest):
    if body.machine_id not in service.twins: raise HTTPException(status_code=404,detail='digital twin not found')
    return asdict(service.simulate(body))
@router.post('/predictive/fusion')
def fusion(body:FusionRequest): return service.fusion.fuse(body.modalities)
@router.post('/predictive/rul')
def rul(body:RULRequest): return service.rul.estimate(body.health_score,body.drift_score,body.max_hours)
