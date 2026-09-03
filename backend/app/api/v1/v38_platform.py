from fastapi import APIRouter
from app.platform_v38.release import V38Evidence,V38ReleaseGate
router=APIRouter(prefix="/platform/v38",tags=["platform-v3.8"] )
@router.get("/capabilities")
async def capabilities():
    return {"version":"3.8.0","focus":"platform consolidation","capabilities":["failure-engineering","distributed-runtime","event-driven-streaming","fleet-intelligence","mlops","advanced-failure-intelligence","agentic-maintenance","enterprise-integration","security","observability","benchmarking"]}
@router.post("/release-gate")
async def release_gate(evidence:dict):
    allowed={k:bool(v) for k,v in evidence.items() if k in V38Evidence.__dataclass_fields__}
    return V38ReleaseGate().evaluate(V38Evidence(**allowed))
