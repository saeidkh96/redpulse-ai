from fastapi import APIRouter, HTTPException
from app.schemas.industrial_ai import (
    KnowledgeIngestRequest, CopilotRequest, AgentRunRequest, ApprovalRequest
)
from app.services.industrial_ai import industrial_ai_service

router = APIRouter(prefix="/industrial-ai", tags=["Industrial AI"])

@router.post("/knowledge/ingest")
def ingest(body: KnowledgeIngestRequest):
    return industrial_ai_service.ingest(body.source_id, body.text, body.metadata)

@router.post("/copilot/ask")
def ask(body: CopilotRequest):
    return industrial_ai_service.ask(body)

@router.post("/agents/runs")
def create_run(body: AgentRunRequest):
    run = industrial_ai_service.agents.create(body.objective)
    return {"run_id": run.run_id, "status": run.status, "plan": industrial_ai_service.planner.plan(body.objective)}

@router.post("/agents/runs/{run_id}/approval-required")
def require_approval(run_id: str):
    try:
        run = industrial_ai_service.agents.runs[run_id]
        industrial_ai_service.agents.require_approval(run, "maintenance action requires approval")
        return {"run_id": run.run_id, "status": run.status}
    except KeyError as exc:
        raise HTTPException(404, "run not found") from exc

@router.post("/agents/runs/{run_id}/approve")
def approve(run_id: str, body: ApprovalRequest):
    try:
        run = industrial_ai_service.agents.approve(run_id, body.actor)
        return {"run_id": run.run_id, "status": run.status, "audit": run.audit}
    except KeyError as exc:
        raise HTTPException(404, "run not found") from exc

@router.get("/agents/runs/{run_id}")
def get_run(run_id: str):
    try:
        run = industrial_ai_service.agents.runs[run_id]
        return {
            "run_id": run.run_id,
            "objective": run.objective,
            "status": run.status,
            "steps": run.steps,
            "audit": run.audit,
        }
    except KeyError as exc:
        raise HTTPException(404, "run not found") from exc
