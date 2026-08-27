import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.maintenance.verification import (
    MaintenanceSnapshot,
    MaintenanceVerification,
    maintenance_verification_engine,
)
from app.services.machine_health import (
    MachineHealthResult,
    machine_health_service,
)


@dataclass(frozen=True)
class MaintenanceVerificationResult:
    machine_id: uuid.UUID
    before: MaintenanceSnapshot
    after: MaintenanceSnapshot
    verification: MaintenanceVerification


class MaintenanceVerificationService:
    async def verify(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        before: MaintenanceSnapshot,
        machine_type: str | None = None,
        event_limit: int = 100,
        library_limit: int = 500,
    ) -> MaintenanceVerificationResult:
        if event_limit < 1:
            raise ValueError(
                "event_limit must be at least 1"
            )

        if library_limit < 1:
            raise ValueError(
                "library_limit must be at least 1"
            )

        health_result = (
            await machine_health_service.assess(
                session,
                machine_id=machine_id,
                machine_type=machine_type,
                event_limit=event_limit,
                library_limit=library_limit,
            )
        )

        after = self._snapshot_from_health(
            health_result
        )

        verification = (
            maintenance_verification_engine.verify(
                before=before,
                after=after,
            )
        )

        return MaintenanceVerificationResult(
            machine_id=machine_id,
            before=before,
            after=after,
            verification=verification,
        )

    @staticmethod
    def _snapshot_from_health(
        result: MachineHealthResult,
    ) -> MaintenanceSnapshot:
        return MaintenanceSnapshot(
            health_score=(
                result.health.health_score
            ),
            risk_score=(
                result.health.risk_score
            ),
            deviation_score=(
                result.deviation_score
            ),
            drift_score=(
                result.drift_score
            ),
            failure_match_score=(
                result.failure_match_score
            ),
        )


maintenance_verification_service = (
    MaintenanceVerificationService()
)
