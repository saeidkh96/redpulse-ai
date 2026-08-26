import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.machine import machine_repository
from app.schemas.drift import DriftAnalysisRead
from app.services.behavioral_memory import (
    behavioral_memory_service,
)
from app.services.drift_analysis import (
    DriftBaselineNotFoundError,
    DriftTelemetryError,
    drift_analysis_service,
)


router = APIRouter(
    prefix="/machines",
    tags=["slow-drift"],
)


@router.post(
    "/{machine_id}/drift/analyze",
    response_model=DriftAnalysisRead,
    status_code=status.HTTP_200_OK,
)
async def analyze_slow_drift(
    machine_id: uuid.UUID,
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> DriftAnalysisRead:
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
        result = await drift_analysis_service.analyze(
            session,
            machine_id,
        )

    except DriftBaselineNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except DriftTelemetryError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )

    first_window = result.windows[0]
    last_window = result.windows[-1]

    await behavioral_memory_service.record_drift(
        session,
        machine_id=machine_id,
        baseline_version=result.baseline_version,
        window_start=first_window.window_start,
        window_end=last_window.window_end,
        overall_score=(
            result.drift_report.overall_score
        ),
        state=result.drift_report.state,
        signals=result.drift_report.signals,
    )

    return DriftAnalysisRead(
        machine_id=machine_id,
        baseline_version=result.baseline_version,
        window_size=result.window_size,
        window_count=result.window_count,
        overall_score=(
            result.drift_report.overall_score
        ),
        state=result.drift_report.state,
        windows=[
            {
                "index": window.index,
                "window_start": window.window_start,
                "window_end": window.window_end,
                "sample_count": window.sample_count,
                "deviation_score": window.deviation_score,
                "severity": window.severity,
            }
            for window in result.windows
        ],
        signals=result.drift_report.signals,
    )
