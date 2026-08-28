from fastapi import APIRouter, HTTPException
from app.schemas.production_platform import ApprovalRequest, ApprovalDecisionRequest, JobSubmitRequest, DriftRequest, QualityRequest, FleetPartitionRequest
from app.services.production_platform import production_platform_service as service
router=APIRouter(prefix="/production-platform",tags=["Production Platform"])
@router.get("/readiness")
def readiness(): return service.readiness()
@router.post("/approvals")
def request_approval(body:ApprovalRequest):
    a=service.platform.approvals.request(body.tenant_id,body.action); return {"approval_id":a.approval_id,"approved":a.approved}
@router.post("/approvals/{approval_id}/decision")
def decide(approval_id:str,body:ApprovalDecisionRequest):
    try: a=service.platform.approvals.decide(approval_id,body.approved,body.actor)
    except KeyError as e: raise HTTPException(404,"approval not found") from e
    return {"approval_id":a.approval_id,"approved":a.approved,"actor":a.actor}
@router.post("/jobs")
def submit_job(body:JobSubmitRequest):
    j=service.platform.automation.submit(body.tenant_id,body.provider,body.event_type,body.payload); return {"job_id":j.job_id,"status":j.status}
@router.post("/ml/drift/evaluate")
def drift(body:DriftRequest): return service.drift(body.model,body.score,body.threshold)
@router.post("/data/quality")
def quality(body:QualityRequest): return service.quality(body.record,body.required)
@router.post("/fleet/partitions")
def partitions(body:FleetPartitionRequest): return service.partitions(body.machine_ids,body.partitions)
