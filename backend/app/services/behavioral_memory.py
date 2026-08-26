import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.engine import behavioral_memory_engine
from app.models.behavior_event import BehaviorEvent
from app.repositories.behavior_event import (
    behavior_event_repository,
)


class BehavioralMemoryService:
    async def record_deviation(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        baseline_version: str,
        window_start: datetime,
        window_end: datetime,
        overall_score: float,
        severity: str,
        sensor_deviations: dict,
        correlation_shifts: dict,
    ) -> BehaviorEvent | None:
        decision = behavioral_memory_engine.from_deviation(
            overall_score=overall_score,
            severity=severity,
            sensor_deviations=sensor_deviations,
            correlation_shifts=correlation_shifts,
        )

        if not decision.should_store:
            return None

        existing = (
            await behavior_event_repository.find_matching_event(
                session,
                machine_id=machine_id,
                event_type=decision.event_type,
                baseline_version=baseline_version,
                window_start=window_start,
                window_end=window_end,
            )
        )

        if existing is not None:
            return existing

        return await behavior_event_repository.create(
            session,
            machine_id=machine_id,
            event_type=decision.event_type,
            severity=decision.severity,
            score=overall_score,
            baseline_version=baseline_version,
            window_start=window_start,
            window_end=window_end,
            summary=decision.summary,
            evidence=decision.evidence,
        )

    async def record_drift(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        baseline_version: str,
        window_start: datetime,
        window_end: datetime,
        overall_score: float,
        state: str,
        signals: dict,
    ) -> BehaviorEvent | None:
        decision = behavioral_memory_engine.from_drift(
            overall_score=overall_score,
            state=state,
            signals=signals,
        )

        if not decision.should_store:
            return None

        existing = (
            await behavior_event_repository.find_matching_event(
                session,
                machine_id=machine_id,
                event_type=decision.event_type,
                baseline_version=baseline_version,
                window_start=window_start,
                window_end=window_end,
            )
        )

        if existing is not None:
            return existing

        return await behavior_event_repository.create(
            session,
            machine_id=machine_id,
            event_type=decision.event_type,
            severity=decision.severity,
            score=overall_score,
            baseline_version=baseline_version,
            window_start=window_start,
            window_end=window_end,
            summary=decision.summary,
            evidence=decision.evidence,
        )

    async def list_history(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        event_type=None,
        severity=None,
        limit: int = 100,
    ) -> list[BehaviorEvent]:
        return await behavior_event_repository.list_for_machine(
            session,
            machine_id,
            event_type=event_type,
            severity=severity,
            limit=limit,
        )

    async def get_event(
        self,
        session: AsyncSession,
        event_id: uuid.UUID,
    ) -> BehaviorEvent | None:
        return await behavior_event_repository.get_by_id(
            session,
            event_id,
        )


behavioral_memory_service = BehavioralMemoryService()
