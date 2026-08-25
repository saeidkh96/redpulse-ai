import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.machine import machine_repository
from app.repositories.machine_baseline import (
    machine_baseline_repository,
)
from app.schemas.machine_baseline import MachineBaselineRead
from app.services.machine_dna import machine_dna_service


router = APIRouter(
    prefix="/machines",
    tags=["machine-dna"],
)


@router.post(
    "/{machine_id}/dna/build",
    response_model=MachineBaselineRead,
    status_code=status.HTTP_201_CREATED,
)
async def build_machine_dna(
    machine_id: uuid.UUID,
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> MachineBaselineRead:
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
        baseline = (
            await machine_dna_service.build_baseline(
                session,
                machine_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )

    return MachineBaselineRead.model_validate(
        baseline
    )


@router.get(
    "/{machine_id}/dna",
    response_model=MachineBaselineRead,
)
async def get_machine_dna(
    machine_id: uuid.UUID,
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> MachineBaselineRead:
    baseline = (
        await machine_baseline_repository.get_latest(
            session,
            machine_id,
        )
    )

    if baseline is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine DNA not found",
        )

    return MachineBaselineRead.model_validate(
        baseline
    )
