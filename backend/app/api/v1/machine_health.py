import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.machine import machine_repository
from app.schemas.machine_health import MachineHealthResponse
from app.services.machine_health import machine_health_service


router = APIRouter(
    prefix="/machines",
    tags=["machine-health"],
)


@router.get(
    "/{machine_id}/health",
    response_model=MachineHealthResponse,
)
async def get_machine_health(
    machine_id: uuid.UUID,
    event_limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    library_limit: int = Query(
        default=500,
        ge=1,
        le=1000,
    ),
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> MachineHealthResponse:
    machine = await machine_repository.get_by_id(
        session,
        machine_id,
    )

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found",
        )

    try:
        result = await machine_health_service.assess(
            session,
            machine_id=machine_id,
            machine_type=machine.machine_type,
            event_limit=event_limit,
            library_limit=library_limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    best_failure_match = None

    if result.best_failure_match is not None:
        match = result.best_failure_match
        fingerprint = match.fingerprint

        best_failure_match = {
            "fingerprint_id": fingerprint.id,
            "machine_id": fingerprint.machine_id,
            "failure_type": fingerprint.failure_type,
            "machine_type": fingerprint.machine_type,
            "title": fingerprint.title,
            "confidence": fingerprint.confidence,
            "failure_time": fingerprint.failure_time,
            "overall_similarity": (
                match.score.overall_similarity
            ),
        }

    return MachineHealthResponse(
        machine_id=result.machine_id,
        health={
            "health_score": result.health.health_score,
            "risk_score": result.health.risk_score,
            "state": result.health.state,
            "early_warning": result.health.early_warning,
            "components": result.health.components,
        },
        persistence={
            "score": result.persistence.score,
            "event_count": result.persistence.event_count,
            "deviation_count": (
                result.persistence.deviation_count
            ),
            "drift_count": result.persistence.drift_count,
            "anomalous_count": (
                result.persistence.anomalous_count
            ),
            "duration_seconds": (
                result.persistence.duration_seconds
            ),
        },
        deviation_score=result.deviation_score,
        drift_score=result.drift_score,
        failure_match_score=result.failure_match_score,
        best_failure_match=best_failure_match,
    )
