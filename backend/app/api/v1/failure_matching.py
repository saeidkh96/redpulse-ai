import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.machine import machine_repository
from app.schemas.failure_match import (
    FailureMatchingRequest,
    FailureMatchingResponse,
)
from app.services.failure_matching import (
    failure_matching_service,
)


router = APIRouter(
    prefix="/machines",
    tags=["failure-matching"],
)


@router.post(
    "/{machine_id}/failures/match",
    response_model=FailureMatchingResponse,
    status_code=status.HTTP_200_OK,
)
async def match_failure_trajectory(
    machine_id: uuid.UUID,
    payload: FailureMatchingRequest,
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> FailureMatchingResponse:
    machine = await machine_repository.get_by_id(
        session,
        machine_id,
    )

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found",
        )

    machine_type = (
        payload.machine_type
        if payload.machine_type is not None
        else machine.machine_type
    )

    try:
        result = (
            await failure_matching_service.match_machine(
                session,
                machine_id=machine_id,
                machine_type=machine_type,
                failure_type=payload.failure_type,
                event_limit=payload.event_limit,
                library_limit=payload.library_limit,
                top_k=payload.top_k,
                minimum_similarity=(
                    payload.minimum_similarity
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    matches = [
        {
            "fingerprint_id": (
                match.fingerprint.id
            ),
            "machine_id": (
                match.fingerprint.machine_id
            ),
            "failure_type": (
                match.fingerprint.failure_type
            ),
            "machine_type": (
                match.fingerprint.machine_type
            ),
            "title": (
                match.fingerprint.title
            ),
            "confidence": (
                match.fingerprint.confidence
            ),
            "failure_time": (
                match.fingerprint.failure_time
            ),
            "score": {
                "overall_similarity": (
                    match.score.overall_similarity
                ),
                "sensor_similarity": (
                    match.score.sensor_similarity
                ),
                "deviation_similarity": (
                    match.score.deviation_similarity
                ),
                "drift_similarity": (
                    match.score.drift_similarity
                ),
                "correlation_similarity": (
                    match.score.correlation_similarity
                ),
                "trajectory_similarity": (
                    match.score.trajectory_similarity
                ),
            },
        }
        for match in result.matches
    ]

    return FailureMatchingResponse(
        machine_id=result.machine_id,
        candidate_count=result.candidate_count,
        match_count=len(matches),
        matches=matches,
    )
