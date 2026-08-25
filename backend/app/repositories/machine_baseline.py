import uuid
from datetime import datetime

from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.machine_baseline import MachineBaseline


class MachineBaselineRepository:
    async def create(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        sample_count: int,
        window_start: datetime,
        window_end: datetime,
        sensor_features: dict,
        correlations: dict,
        baseline_version: str,
    ) -> MachineBaseline:
        baseline = MachineBaseline(
            machine_id=machine_id,
            baseline_version=baseline_version,
            sample_count=sample_count,
            window_start=window_start,
            window_end=window_end,
            sensor_features=sensor_features,
            correlations=correlations,
        )

        session.add(baseline)
        await session.commit()
        await session.refresh(baseline)

        return baseline

    async def get_latest(
        self,
        session: AsyncSession,
        machine_id: uuid.UUID,
    ) -> MachineBaseline | None:
        statement = (
            select(MachineBaseline)
            .where(
                MachineBaseline.machine_id == machine_id
            )
            .order_by(
                MachineBaseline.created_at.desc(),
                MachineBaseline.baseline_version.cast(Integer).desc(),
            )
            .limit(1)
        )

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def get_next_version(
        self,
        session: AsyncSession,
        machine_id: uuid.UUID,
    ) -> str:
        statement = (
            select(
                func.max(
                    MachineBaseline.baseline_version.cast(Integer)
                )
            )
            .where(
                MachineBaseline.machine_id == machine_id
            )
        )

        result = await session.execute(statement)
        current_version = result.scalar_one_or_none()

        if current_version is None:
            return "1"

        return str(current_version + 1)


machine_baseline_repository = MachineBaselineRepository()
