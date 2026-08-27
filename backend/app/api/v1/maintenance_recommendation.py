import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.maintenance_recommendation import (
    MaintenanceDecisionResponse,
    MaintenanceRecommendationResponse,
)
from app.services.maintenance_recommendation import (
    maintenance_recommendation_service,
)


router = APIRouter()


@router.get(
    "/machines/{machine_id}/maintenance-recommendation",
    response_model=MaintenanceRecommendationResponse,
)
async def get_maintenance_recommendation(
    machine_id: uuid.UUID,
    machine_type: str | None = Query(
        default=None,
    ),
    event_limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    library_limit: int = Query(
        default=500,
        ge=1,
        le=5000,
    ),
    session: AsyncSession = Depends(get_db_session),
) -> MaintenanceRecommendationResponse:
    try:
        result = (
            await maintenance_recommendation_service.recommend(
                session,
                machine_id=machine_id,
                machine_type=machine_type,
                event_limit=event_limit,
                library_limit=library_limit,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    decision = result.decision

    return MaintenanceRecommendationResponse(
        machine_id=result.machine_id,
        decision=MaintenanceDecisionResponse(
            priority=decision.priority,
            action_type=decision.action_type,
            urgency_score=decision.urgency_score,
            recommended_action=(
                decision.recommended_action
            ),
            predicted_failure=(
                decision.predicted_failure
            ),
            affected_signals=(
                decision.affected_signals
            ),
            root_cause_hints=(
                decision.root_cause_hints
            ),
            rationale=decision.rationale,
        ),
    )

