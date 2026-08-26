import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.failure.fingerprint import (
    failure_fingerprint_builder,
)
from app.models.behavior_event import BehaviorEventType
from app.models.failure_fingerprint import FailureFingerprint
from app.repositories.behavior_event import (
    behavior_event_repository,
)
from app.repositories.failure_fingerprint import (
    failure_fingerprint_repository,
)


class FailureLibraryService:
    async def create_from_memory(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        failure_type: str,
        title: str,
        machine_type: str | None = None,
        description: str | None = None,
        confidence: float | None = None,
        failure_time: datetime | None = None,
        event_limit: int = 100,
    ) -> FailureFingerprint:
        events = await behavior_event_repository.list_for_machine(
            session,
            machine_id,
            limit=event_limit,
        )

        relevant_events = [
            event
            for event in events
            if event.event_type
            in {
                BehaviorEventType.DEVIATION,
                BehaviorEventType.DRIFT,
            }
        ]

        if not relevant_events:
            raise ValueError(
                "No behavioral memory events available "
                "for failure fingerprint creation"
            )

        fingerprint = (
            failure_fingerprint_builder.build(
                relevant_events
            )
        )

        return await failure_fingerprint_repository.create(
            session,
            machine_id=machine_id,
            failure_type=failure_type,
            machine_type=machine_type,
            title=title,
            description=description,
            confidence=confidence,
            baseline_version=(
                fingerprint.baseline_version
            ),
            trajectory_start=(
                fingerprint.trajectory_start
            ),
            trajectory_end=(
                fingerprint.trajectory_end
            ),
            failure_time=failure_time,
            dominant_sensors=(
                fingerprint.dominant_sensors
            ),
            deviation_signature=(
                fingerprint.deviation_signature
            ),
            drift_signature=(
                fingerprint.drift_signature
            ),
            correlation_signature=(
                fingerprint.correlation_signature
            ),
            trajectory_summary=(
                fingerprint.trajectory_summary
            ),
            evidence=(
                fingerprint.evidence
            ),
        )

    async def get(
        self,
        session: AsyncSession,
        fingerprint_id: uuid.UUID,
    ) -> FailureFingerprint | None:
        return await failure_fingerprint_repository.get_by_id(
            session,
            fingerprint_id,
        )

    async def list_for_machine(
        self,
        session: AsyncSession,
        machine_id: uuid.UUID,
        *,
        limit: int = 100,
    ) -> list[FailureFingerprint]:
        return await failure_fingerprint_repository.list_for_machine(
            session,
            machine_id,
            limit=limit,
        )

    async def list_library(
        self,
        session: AsyncSession,
        *,
        failure_type: str | None = None,
        machine_type: str | None = None,
        limit: int = 100,
    ) -> list[FailureFingerprint]:
        return await failure_fingerprint_repository.list_library(
            session,
            failure_type=failure_type,
            machine_type=machine_type,
            limit=limit,
        )


failure_library_service = FailureLibraryService()
