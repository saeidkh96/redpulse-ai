import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.counterfactual_maintenance import (
    CounterfactualMaintenanceRequest,
    CounterfactualMaintenanceResponse,
    CounterfactualOutcomeResponse,
)
from app.schemas.maintenance_verification import MaintenanceSnapshotResponse
from app.services.counterfactual_maintenance import (
    counterfactual_maintenance_service,
)


router = APIRouter(tags=["counterfactual-maintenance"])


@router.post(
    "/machines/{machine_id}/counterfactual-maintenance",
    response_model=CounterfactualMaintenanceResponse,
)
async def analyze_counterfactual_maintenance(
    machine_id: uuid.UUID,
    body: CounterfactualMaintenanceRequest,
    session: AsyncSession = Depends(get_db_session),
) -> CounterfactualMaintenanceResponse:
    try:
        result = await counterfactual_maintenance_service.analyze(
            session,
            machine_id=machine_id,
            machine_type=body.machine_type,
            candidate_interventions=body.candidate_interventions,
            horizon_steps=body.horizon_steps,
            event_limit=body.event_limit,
            library_limit=body.library_limit,
            history_limit=body.history_limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    analysis = result.analysis

    return CounterfactualMaintenanceResponse(
        machine_id=result.machine_id,
        current=MaintenanceSnapshotResponse(
            health_score=analysis.current.health_score,
            risk_score=analysis.current.risk_score,
            deviation_score=analysis.current.deviation_score,
            drift_score=analysis.current.drift_score,
            failure_match_score=analysis.current.failure_match_score,
        ),
        no_maintenance=CounterfactualOutcomeResponse(
            **analysis.no_maintenance.__dict__
        ),
        candidates=[
            CounterfactualOutcomeResponse(**candidate.__dict__)
            for candidate in analysis.candidates
        ],
        recommended_intervention=analysis.recommended_intervention,
        recommendation_confidence=analysis.recommendation_confidence,
        horizon_steps=analysis.horizon_steps,
        evidence_note=result.evidence_note,
    )
