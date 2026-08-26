import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.behavior_event import (
    BehaviorEvent,
    BehaviorEventType,
    BehaviorSeverity,
)


class BehaviorEventRepository:
    async def create(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        event_type: BehaviorEventType,
        severity: BehaviorSeverity,
        score: float | None,
        baseline_version: str | None,
        window_start: datetime | None,
        window_end: datetime | None,
        summary: str | None,
        evidence: dict,
    ) -> BehaviorEvent:
        event = BehaviorEvent(
            machine_id=machine_id,
            event_type=event_type,
            severity=severity,
            score=score,
            baseline_version=baseline_version,
            window_start=window_start,
            window_end=window_end,
            summary=summary,
            evidence=evidence,
        )

        session.add(event)

        await session.commit()
        await session.refresh(event)

        return event

    async def find_matching_event(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        event_type: BehaviorEventType,
        baseline_version: str | None,
        window_start: datetime | None,
        window_end: datetime | None,
    ) -> BehaviorEvent | None:
        statement = select(
            BehaviorEvent
        ).where(
            BehaviorEvent.machine_id == machine_id,
            BehaviorEvent.event_type == event_type,
            BehaviorEvent.baseline_version == baseline_version,
            BehaviorEvent.window_start == window_start,
            BehaviorEvent.window_end == window_end,
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def list_for_machine(
        self,
        session: AsyncSession,
        machine_id: uuid.UUID,
        *,
        event_type: BehaviorEventType | None = None,
        severity: BehaviorSeverity | None = None,
        limit: int = 100,
    ) -> list[BehaviorEvent]:
        statement = (
            select(BehaviorEvent)
            .where(
                BehaviorEvent.machine_id == machine_id
            )
            .order_by(
                BehaviorEvent.created_at.desc()
            )
            .limit(limit)
        )

        if event_type is not None:
            statement = statement.where(
                BehaviorEvent.event_type == event_type
            )

        if severity is not None:
            statement = statement.where(
                BehaviorEvent.severity == severity
            )

        result = await session.execute(statement)

        return list(result.scalars().all())

    async def get_by_id(
        self,
        session: AsyncSession,
        event_id: uuid.UUID,
    ) -> BehaviorEvent | None:
        statement = select(
            BehaviorEvent
        ).where(
            BehaviorEvent.id == event_id
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()


behavior_event_repository = BehaviorEventRepository()
