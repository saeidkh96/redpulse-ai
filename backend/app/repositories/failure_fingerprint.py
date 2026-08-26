import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.failure_fingerprint import FailureFingerprint


class FailureFingerprintRepository:
    async def create(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        failure_type: str,
        machine_type: str | None,
        title: str,
        description: str | None,
        confidence: float | None,
        baseline_version: str | None,
        trajectory_start,
        trajectory_end,
        failure_time,
        dominant_sensors: list,
        deviation_signature: dict,
        drift_signature: dict,
        correlation_signature: dict,
        trajectory_summary: dict,
        evidence: dict,
    ) -> FailureFingerprint:
        fingerprint = FailureFingerprint(
            machine_id=machine_id,
            failure_type=failure_type,
            machine_type=machine_type,
            title=title,
            description=description,
            confidence=confidence,
            baseline_version=baseline_version,
            trajectory_start=trajectory_start,
            trajectory_end=trajectory_end,
            failure_time=failure_time,
            dominant_sensors=dominant_sensors,
            deviation_signature=deviation_signature,
            drift_signature=drift_signature,
            correlation_signature=correlation_signature,
            trajectory_summary=trajectory_summary,
            evidence=evidence,
        )

        session.add(fingerprint)

        await session.commit()
        await session.refresh(fingerprint)

        return fingerprint

    async def get_by_id(
        self,
        session: AsyncSession,
        fingerprint_id: uuid.UUID,
    ) -> FailureFingerprint | None:
        statement = select(
            FailureFingerprint
        ).where(
            FailureFingerprint.id == fingerprint_id
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def list_for_machine(
        self,
        session: AsyncSession,
        machine_id: uuid.UUID,
        *,
        limit: int = 100,
    ) -> list[FailureFingerprint]:
        statement = (
            select(FailureFingerprint)
            .where(
                FailureFingerprint.machine_id
                == machine_id
            )
            .order_by(
                FailureFingerprint.created_at.desc()
            )
            .limit(limit)
        )

        result = await session.execute(statement)

        return list(
            result.scalars().all()
        )

    async def list_library(
        self,
        session: AsyncSession,
        *,
        failure_type: str | None = None,
        machine_type: str | None = None,
        limit: int = 100,
    ) -> list[FailureFingerprint]:
        statement = select(
            FailureFingerprint
        )

        if failure_type is not None:
            statement = statement.where(
                FailureFingerprint.failure_type
                == failure_type
            )

        if machine_type is not None:
            statement = statement.where(
                FailureFingerprint.machine_type
                == machine_type
            )

        statement = statement.order_by(
            FailureFingerprint.created_at.desc()
        ).limit(limit)

        result = await session.execute(statement)

        return list(
            result.scalars().all()
        )


failure_fingerprint_repository = (
    FailureFingerprintRepository()
)
