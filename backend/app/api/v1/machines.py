import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.machine import machine_repository
from app.schemas.machine import (
    MachineCreate,
    MachineRead,
    MachineUpdate,
)


router = APIRouter(
    prefix="/machines",
    tags=["machines"],
)


@router.post(
    "",
    response_model=MachineRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_machine(
    payload: MachineCreate,
    session: AsyncSession = Depends(get_db_session),
) -> MachineRead:
    existing = await machine_repository.get_by_code(
        session,
        payload.machine_code,
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Machine code already exists",
        )

    try:
        machine = await machine_repository.create(session, payload)
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Machine code already exists",
        )

    return MachineRead.model_validate(machine)


@router.get(
    "",
    response_model=list[MachineRead],
)
async def list_machines(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
) -> list[MachineRead]:
    machines = await machine_repository.list(
        session,
        offset=offset,
        limit=limit,
    )

    return [
        MachineRead.model_validate(machine)
        for machine in machines
    ]


@router.get(
    "/{machine_id}",
    response_model=MachineRead,
)
async def get_machine(
    machine_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> MachineRead:
    machine = await machine_repository.get_by_id(
        session,
        machine_id,
    )

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found",
        )

    return MachineRead.model_validate(machine)


@router.patch(
    "/{machine_id}",
    response_model=MachineRead,
)
async def update_machine(
    machine_id: uuid.UUID,
    payload: MachineUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> MachineRead:
    machine = await machine_repository.get_by_id(
        session,
        machine_id,
    )

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found",
        )

    machine = await machine_repository.update(
        session,
        machine,
        payload,
    )

    return MachineRead.model_validate(machine)
