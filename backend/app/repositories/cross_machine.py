import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.machine import Machine
from app.models.maintenance_intervention import MaintenanceIntervention


class CrossMachineRepository:
    async def get_machine(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
    ) -> Machine | None:
        result = await session.execute(
            select(Machine).where(Machine.id == machine_id)
        )
        return result.scalar_one_or_none()

    async def list_peer_machines(
        self,
        session: AsyncSession,
        *,
        target: Machine,
        limit: int = 100,
    ) -> list[Machine]:
        stmt = select(Machine).where(Machine.id != target.id)

        if target.machine_type is not None:
            stmt = stmt.where(Machine.machine_type == target.machine_type)

        stmt = stmt.order_by(Machine.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def list_completed_interventions_for_machines(
        self,
        session: AsyncSession,
        *,
        machine_ids: list[uuid.UUID],
        limit: int = 1000,
    ) -> list[MaintenanceIntervention]:
        if not machine_ids:
            return []

        stmt = (
            select(MaintenanceIntervention)
            .where(
                MaintenanceIntervention.machine_id.in_(machine_ids),
                MaintenanceIntervention.status == "completed",
            )
            .order_by(MaintenanceIntervention.completed_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


cross_machine_repository = CrossMachineRepository()
