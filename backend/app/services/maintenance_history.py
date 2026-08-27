import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.maintenance.verification import MaintenanceSnapshot
from app.models.maintenance_intervention import MaintenanceIntervention
from app.repositories.maintenance_intervention import maintenance_intervention_repository
from app.services.maintenance_verification import maintenance_verification_service


def snapshot_to_dict(snapshot: MaintenanceSnapshot) -> dict:
    return {
        "health_score": snapshot.health_score,
        "risk_score": snapshot.risk_score,
        "deviation_score": snapshot.deviation_score,
        "drift_score": snapshot.drift_score,
        "failure_match_score": snapshot.failure_match_score,
    }


def verification_to_dict(verification) -> dict:
    state = verification.state.value if hasattr(verification.state, "value") else str(verification.state)
    return {
        "recovery_score": verification.recovery_score,
        "state": state,
        "health_improvement": verification.health_improvement,
        "risk_reduction": verification.risk_reduction,
        "deviation_reduction": verification.deviation_reduction,
        "drift_reduction": verification.drift_reduction,
        "failure_match_reduction": verification.failure_match_reduction,
        "components": verification.components,
    }


class MaintenanceHistoryService:
    async def create(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        machine_type: str | None,
        intervention_type: str,
        failure_prediction: dict,
        recommendation: dict,
        technician_notes: str | None,
        before: MaintenanceSnapshot,
        started_at: datetime | None,
    ) -> MaintenanceIntervention:
        return await maintenance_intervention_repository.create(
            session,
            machine_id=machine_id,
            machine_type=machine_type,
            intervention_type=intervention_type,
            status="in_progress" if started_at is not None else "planned",
            failure_prediction=failure_prediction,
            recommendation=recommendation,
            technician_notes=technician_notes,
            before_snapshot=snapshot_to_dict(before),
            started_at=started_at,
        )

    async def get(
        self,
        session: AsyncSession,
        intervention_id: uuid.UUID,
    ) -> MaintenanceIntervention:
        record = await maintenance_intervention_repository.get_by_id(
            session, intervention_id
        )
        if record is None:
            raise ValueError("maintenance intervention not found")
        return record

    async def list_for_machine(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        limit: int = 100,
    ) -> list[MaintenanceIntervention]:
        return await maintenance_intervention_repository.list_for_machine(
            session, machine_id, limit=limit
        )

    async def complete_and_verify(
        self,
        session: AsyncSession,
        *,
        intervention_id: uuid.UUID,
        event_limit: int = 100,
        library_limit: int = 500,
    ):
        record = await self.get(session, intervention_id)
        if record.status == "completed":
            raise ValueError("maintenance intervention is already completed")
        if record.status == "cancelled":
            raise ValueError("cancelled maintenance intervention cannot be completed")

        before = MaintenanceSnapshot(**record.before_snapshot)

        result = await maintenance_verification_service.verify(
            session,
            machine_id=record.machine_id,
            before=before,
            machine_type=record.machine_type,
            event_limit=event_limit,
            library_limit=library_limit,
        )

        verification = result.verification
        verification_dict = verification_to_dict(verification)

        outcome_label = self._outcome_label(verification.recovery_score)
        updated = await maintenance_intervention_repository.update_state(
            session,
            record=record,
            status="completed",
            completed_at=datetime.now(timezone.utc),
            after_snapshot=snapshot_to_dict(result.after),
            verification_result=verification_dict,
            outcome_label=outcome_label,
            outcome_score=verification.recovery_score,
            outcome_evidence={
                "risk_reduction": verification.risk_reduction,
                "drift_reduction": verification.drift_reduction,
                "health_improvement": verification.health_improvement,
                "deviation_reduction": verification.deviation_reduction,
                "failure_match_reduction": verification.failure_match_reduction,
            },
        )

        return updated, result

    @staticmethod
    def _outcome_label(score: float) -> str:
        if score >= 0.55:
            return "highly_effective"
        if score >= 0.25:
            return "effective"
        if score >= 0.08:
            return "limited_effect"
        if score >= -0.08:
            return "ineffective"
        return "negative"


maintenance_history_service = MaintenanceHistoryService()
