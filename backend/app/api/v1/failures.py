import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.machine import machine_repository
from app.schemas.failure_fingerprint import (
    FailureFingerprintCreate,
    FailureFingerprintListResponse,
    FailureFingerprintResponse,
)
from app.services.failure_library import (
    failure_library_service,
)


router = APIRouter(
    tags=["failure-fingerprints"],
)


@router.post(
    "/machines/{machine_id}/failures/fingerprints",
    response_model=FailureFingerprintResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_failure_fingerprint(
    machine_id: uuid.UUID,
    payload: FailureFingerprintCreate,
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> FailureFingerprintResponse:
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
        fingerprint = (
            await failure_library_service.create_from_memory(
                session,
                machine_id=machine_id,
                failure_type=payload.failure_type,
                machine_type=(
                    payload.machine_type
                    or machine.machine_type
                ),
                title=payload.title,
                description=payload.description,
                confidence=payload.confidence,
                failure_time=payload.failure_time,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return FailureFingerprintResponse.model_validate(
        fingerprint
    )


@router.get(
    "/machines/{machine_id}/failures/fingerprints",
    response_model=FailureFingerprintListResponse,
)
async def list_machine_failure_fingerprints(
    machine_id: uuid.UUID,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> FailureFingerprintListResponse:
    machine = await machine_repository.get_by_id(
        session,
        machine_id,
    )

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found",
        )

    fingerprints = (
        await failure_library_service.list_for_machine(
            session,
            machine_id,
            limit=limit,
        )
    )

    return FailureFingerprintListResponse(
        value=[
            FailureFingerprintResponse.model_validate(
                fingerprint
            )
            for fingerprint in fingerprints
        ],
        Count=len(fingerprints),
    )


@router.get(
    "/failures/fingerprints/{fingerprint_id}",
    response_model=FailureFingerprintResponse,
)
async def get_failure_fingerprint(
    fingerprint_id: uuid.UUID,
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> FailureFingerprintResponse:
    fingerprint = await failure_library_service.get(
        session,
        fingerprint_id,
    )

    if fingerprint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failure fingerprint not found",
        )

    return FailureFingerprintResponse.model_validate(
        fingerprint
    )


@router.get(
    "/failures/fingerprints",
    response_model=FailureFingerprintListResponse,
)
async def list_failure_library(
    failure_type: str | None = Query(
        default=None,
        max_length=150,
    ),
    machine_type: str | None = Query(
        default=None,
        max_length=100,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> FailureFingerprintListResponse:
    fingerprints = (
        await failure_library_service.list_library(
            session,
            failure_type=failure_type,
            machine_type=machine_type,
            limit=limit,
        )
    )

    return FailureFingerprintListResponse(
        value=[
            FailureFingerprintResponse.model_validate(
                fingerprint
            )
            for fingerprint in fingerprints
        ],
        Count=len(fingerprints),
    )
