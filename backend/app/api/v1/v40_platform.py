from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.platform_v40.intelligence import IntelligenceInput, PredictiveMaintenanceEngine
from app.platform_v40.release import V40Evidence, V40ReleaseGate

router = APIRouter(prefix="/platform/v40", tags=["platform-v4.0"])


class IntelligenceRequest(BaseModel):
    machine_id: str
    baseline: list[float] = Field(min_length=1)
    current: list[float] = Field(min_length=1)
    drift_score: float = Field(ge=0, le=1)
    trajectory_match: float = Field(ge=0, le=1)
    uncertainty: float = Field(default=0.1, ge=0, le=1)


@router.get("/capabilities")
async def capabilities() -> dict[str, object]:
    return {
        "version": "4.0.0",
        "focus": "production-grade industrial AI platform",
        "phases": {
            "A": "production-architecture-hardening",
            "B": "distributed-data-streaming",
            "C": "production-mlops",
            "D": "unified-intelligence-orchestration",
            "E": "agentic-maintenance-operations",
            "F": "enterprise-integration",
            "G": "security-governance-sre",
            "H": "evaluation-benchmarking",
            "I": "release-hardening",
        },
    }


@router.post("/intelligence/evaluate")
async def evaluate_intelligence(payload: IntelligenceRequest) -> dict:
    try:
        result = PredictiveMaintenanceEngine().evaluate(
            IntelligenceInput(
                payload.machine_id,
                tuple(payload.baseline),
                tuple(payload.current),
                payload.drift_score,
                payload.trajectory_match,
                payload.uncertainty,
            )
        )
        return asdict(result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/release-gate")
async def release_gate(evidence: dict) -> dict[str, object]:
    allowed = {k: bool(v) for k, v in evidence.items() if k in V40Evidence.__dataclass_fields__}
    return V40ReleaseGate().evaluate(V40Evidence(**allowed))
