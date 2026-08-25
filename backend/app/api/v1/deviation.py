import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.machine import machine_repository
from app.schemas.deviation import DeviationAnalysisRead
from app.services.behavioral_deviation import (
    BaselineNotFoundError,
    InsufficientTelemetryError,
    behavioral_deviation_service,
)


router = APIRouter(
    prefix="/machines",
    tags=["behavioral-deviation"],
)


@router.post(
    "/{machine_id}/deviation/analyze",
    response_model=DeviationAnalysisRead,
    status_code=status.HTTP_200_OK,
)
async def analyze_behavioral_deviation(
    machine_id: uuid.UUID,
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> DeviationAnalysisRead:
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
        result = (
            await behavioral_deviation_service.analyze(
                session,
                machine_id,
            )
        )

    except BaselineNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InsufficientTelemetryError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )

    return DeviationAnalysisRead(
        machine_id=machine_id,
        baseline_version=result.baseline_version,
        sample_count=result.sample_count,
        window_start=result.window_start,
        window_end=result.window_end,
        overall_score=result.report.overall_score,
        severity=result.report.severity,
        sensor_deviations=(
            result.report.sensor_deviations
        ),
        correlation_shifts=(
            result.report.correlation_shifts
        ),
    )
