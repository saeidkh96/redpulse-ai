import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.machine import Machine
from app.schemas.machine import MachineCreate, MachineUpdate


class MachineRepository:
    async def create(
        self,
        session: AsyncSession,
        data: MachineCreate,
    ) -> Machine:
        machine = Machine(
            machine_code=data.machine_code,
            name=data.name,
            manufacturer=data.manufacturer,
            model=data.model,
            machine_type=data.machine_type,
            location=data.location,
            installation_date=data.installation_date,
            status=data.status,
            metadata_=data.metadata,
        )

        session.add(machine)
        await session.commit()
        await session.refresh(machine)

        return machine

    async def get_by_id(
        self,
        session: AsyncSession,
        machine_id: uuid.UUID,
    ) -> Machine | None:
        return await session.get(Machine, machine_id)

    async def get_by_code(
        self,
        session: AsyncSession,
        machine_code: str,
    ) -> Machine | None:
        statement = select(Machine).where(
            Machine.machine_code == machine_code
        )

        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def list(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Machine]:
        statement = (
            select(Machine)
            .order_by(Machine.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(statement)

        return list(result.scalars().all())

    async def update(
        self,
        session: AsyncSession,
        machine: Machine,
        data: MachineUpdate,
    ) -> Machine:
        update_data = data.model_dump(exclude_unset=True)

        if "metadata" in update_data:
            machine.metadata_ = update_data.pop("metadata")

        for field, value in update_data.items():
            setattr(machine, field, value)

        await session.commit()
        await session.refresh(machine)

        return machine


machine_repository = MachineRepository()
