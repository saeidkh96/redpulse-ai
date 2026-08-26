import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.behavior_event import (
    BehaviorEventType,
    BehaviorSeverity,
)
from app.repositories.machine import machine_repository
from app.schemas.behavior_event import BehaviorEventRead
from app.services.behavioral_memory import (
    behavioral_memory_service,
)


router = APIRouter(
    prefix="/machines",
    tags=["behavioral-memory"],
)


@router.get(
    "/{machine_id}/memory",
    response_model=list[BehaviorEventRead],
)
async def list_machine_memory(
    machine_id: uuid.UUID,
    event_type: BehaviorEventType | None = None,
    severity: BehaviorSeverity | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> list[BehaviorEventRead]:
    machine = await machine_repository.get_by_id(
        session,
        machine_id,
    )

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found",
        )

    events = await behavioral_memory_service.list_history(
        session,
        machine_id=machine_id,
        event_type=event_type,
        severity=severity,
        limit=limit,
    )

    return [
        BehaviorEventRead.model_validate(event)
        for event in events
    ]


@router.get(
    "/{machine_id}/memory/{event_id}",
    response_model=BehaviorEventRead,
)
async def get_memory_event(
    machine_id: uuid.UUID,
    event_id: uuid.UUID,
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> BehaviorEventRead:
    machine = await machine_repository.get_by_id(
        session,
        machine_id,
    )

    if machine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found",
        )

    event = await behavioral_memory_service.get_event(
        session,
        event_id,
    )

    if (
        event is None
        or event.machine_id != machine_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Behavior event not found",
        )

    return BehaviorEventRead.model_validate(event)
