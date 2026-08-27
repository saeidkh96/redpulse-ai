import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.maintenance_intervention import MaintenanceIntervention


class MaintenanceInterventionRepository:
    async def create(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        machine_type: str | None,
        intervention_type: str,
        status: str,
        failure_prediction: dict,
        recommendation: dict,
        technician_notes: str | None,
        before_snapshot: dict,
        started_at: datetime | None,
    ) -> MaintenanceIntervention:
        record = MaintenanceIntervention(
            machine_id=machine_id,
            machine_type=machine_type,
            intervention_type=intervention_type,
            status=status,
            failure_prediction=failure_prediction,
            recommendation=recommendation,
            technician_notes=technician_notes,
            before_snapshot=before_snapshot,
            started_at=started_at,
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record

    async def get_by_id(
        self,
        session: AsyncSession,
        intervention_id: uuid.UUID,
    ) -> MaintenanceIntervention | None:
        result = await session.execute(
            select(MaintenanceIntervention).where(
                MaintenanceIntervention.id == intervention_id
            )
        )
        return result.scalar_one_or_none()

    async def list_for_machine(
        self,
        session: AsyncSession,
        machine_id: uuid.UUID,
        *,
        limit: int = 100,
    ) -> list[MaintenanceIntervention]:
        result = await session.execute(
            select(MaintenanceIntervention)
            .where(MaintenanceIntervention.machine_id == machine_id)
            .order_by(MaintenanceIntervention.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_completed(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID | None = None,
        machine_type: str | None = None,
        intervention_type: str | None = None,
        limit: int = 1000,
    ) -> list[MaintenanceIntervention]:
        statement = select(MaintenanceIntervention).where(
            MaintenanceIntervention.status == "completed"
        )
        if machine_id is not None:
            statement = statement.where(MaintenanceIntervention.machine_id == machine_id)
        if machine_type is not None:
            statement = statement.where(MaintenanceIntervention.machine_type == machine_type)
        if intervention_type is not None:
            statement = statement.where(
                MaintenanceIntervention.intervention_type == intervention_type
            )

        result = await session.execute(
            statement.order_by(MaintenanceIntervention.completed_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def update_state(
        self,
        session: AsyncSession,
        *,
        record: MaintenanceIntervention,
        status: str | None = None,
        technician_notes: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        after_snapshot: dict | None = None,
        verification_result: dict | None = None,
        outcome_label: str | None = None,
        outcome_score: float | None = None,
        outcome_evidence: dict | None = None,
    ) -> MaintenanceIntervention:
        if status is not None:
            record.status = status
        if technician_notes is not None:
            record.technician_notes = technician_notes
        if started_at is not None:
            record.started_at = started_at
        if completed_at is not None:
            record.completed_at = completed_at
        if after_snapshot is not None:
            record.after_snapshot = after_snapshot
        if verification_result is not None:
            record.verification_result = verification_result
        if outcome_label is not None:
            record.outcome_label = outcome_label
        if outcome_score is not None:
            record.outcome_score = outcome_score
        if outcome_evidence is not None:
            record.outcome_evidence = outcome_evidence

        await session.commit()
        await session.refresh(record)
        return record


maintenance_intervention_repository = MaintenanceInterventionRepository()
