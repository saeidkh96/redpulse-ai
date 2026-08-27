import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.failure_prediction import (
    FailurePredictionResponse,
    FailureRiskResponse,
)
from app.services.failure_prediction import (
    failure_prediction_service,
)


router = APIRouter(
    tags=["failure-prediction"],
)


@router.get(
    "/machines/{machine_id}/failure-prediction",
    response_model=FailurePredictionResponse,
)
async def get_failure_prediction(
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
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> FailurePredictionResponse:
    try:
        result = await failure_prediction_service.predict(
            session,
            machine_id=machine_id,
            machine_type=machine_type,
            event_limit=event_limit,
            library_limit=library_limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return FailurePredictionResponse(
        machine_id=str(result.machine_id),
        likely_failure_type=(
            result.likely_failure_type
        ),
        likely_failure_title=(
            result.likely_failure_title
        ),
        risk=FailureRiskResponse(
            risk_score=result.risk.risk_score,
            confidence=result.risk.confidence,
            level=result.risk.level.value,
            trend=result.risk.trend.value,
            components=result.risk.components,
        ),
        historical_match_confidence=(
            result.historical_match_confidence
        ),
        failure_match_score=(
            result.failure_match_score
        ),
        evidence=result.evidence,
    )
