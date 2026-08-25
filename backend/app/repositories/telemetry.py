import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telemetry import Telemetry
from app.schemas.telemetry import TelemetryCreate


class TelemetryRepository:
    async def create(
        self,
        session: AsyncSession,
        data: TelemetryCreate,
    ) -> Telemetry:
        measurement = Telemetry(
            machine_id=data.machine_id,
            timestamp=data.timestamp,
            sensor=data.sensor,
            value=data.value,
            unit=data.unit,
        )

        session.add(measurement)
        await session.commit()
        await session.refresh(measurement)

        return measurement

    async def create_batch(
        self,
        session: AsyncSession,
        measurements: list[TelemetryCreate],
    ) -> int:
        rows = [
            Telemetry(
                machine_id=item.machine_id,
                timestamp=item.timestamp,
                sensor=item.sensor,
                value=item.value,
                unit=item.unit,
            )
            for item in measurements
        ]

        session.add_all(rows)
        await session.commit()

        return len(rows)

    async def list_for_machine(
        self,
        session: AsyncSession,
        machine_id: uuid.UUID,
        sensor: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 1000,
    ) -> list[Telemetry]:
        statement = (
            select(Telemetry)
            .where(Telemetry.machine_id == machine_id)
            .order_by(Telemetry.timestamp.desc())
            .limit(limit)
        )

        if sensor is not None:
            statement = statement.where(
                Telemetry.sensor == sensor.strip().lower()
            )

        if start is not None:
            statement = statement.where(
                Telemetry.timestamp >= start
            )

        if end is not None:
            statement = statement.where(
                Telemetry.timestamp <= end
            )

        result = await session.execute(statement)

        return list(result.scalars().all())


telemetry_repository = TelemetryRepository()
