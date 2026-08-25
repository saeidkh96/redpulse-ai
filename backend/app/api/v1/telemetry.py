import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.machine import machine_repository
from app.repositories.telemetry import telemetry_repository
from app.schemas.telemetry import (
    TelemetryBatchCreate,
    TelemetryBatchResult,
    TelemetryCreate,
    TelemetryRead,
)


router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"],
)


@router.post(
    "",
    response_model=TelemetryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_telemetry(
    payload: TelemetryCreate,
    session: AsyncSession = Depends(get_db_session),
) -> TelemetryRead:
    machine = await machine_repository.get_by_id(
        session,
        payload.machine_id,
    )

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found",
        )

    try:
        measurement = await telemetry_repository.create(
            session,
            payload,
        )
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Telemetry measurement already exists",
        )

    return TelemetryRead.model_validate(
        measurement,
        from_attributes=True,
    )


@router.post(
    "/batch",
    response_model=TelemetryBatchResult,
    status_code=status.HTTP_201_CREATED,
)
async def create_telemetry_batch(
    payload: TelemetryBatchCreate,
    session: AsyncSession = Depends(get_db_session),
) -> TelemetryBatchResult:
    machine_ids = {
        item.machine_id
        for item in payload.measurements
    }

    for machine_id in machine_ids:
        machine = await machine_repository.get_by_id(
            session,
            machine_id,
        )

        if machine is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Machine not found: {machine_id}",
            )

    try:
        inserted = await telemetry_repository.create_batch(
            session,
            payload.measurements,
        )
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate telemetry measurement detected",
        )

    return TelemetryBatchResult(inserted=inserted)


@router.get(
    "/machines/{machine_id}",
    response_model=list[TelemetryRead],
)
async def get_machine_telemetry(
    machine_id: uuid.UUID,
    sensor: str | None = Query(default=None, max_length=100),
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(default=1000, ge=1, le=5000),
    session: AsyncSession = Depends(get_db_session),
) -> list[TelemetryRead]:
    machine = await machine_repository.get_by_id(
        session,
        machine_id,
    )

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found",
        )

    if start is not None and end is not None and start > end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="start must be before or equal to end",
        )

    measurements = await telemetry_repository.list_for_machine(
        session,
        machine_id=machine_id,
        sensor=sensor,
        start=start,
        end=end,
        limit=limit,
    )

    return [
        TelemetryRead.model_validate(
            measurement,
            from_attributes=True,
        )
        for measurement in measurements
    ]
