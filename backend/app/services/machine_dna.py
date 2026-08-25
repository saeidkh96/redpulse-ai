import uuid
from collections import defaultdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.engine import feature_engine
from app.models.telemetry import Telemetry
from app.repositories.machine_baseline import (
    machine_baseline_repository,
)


class MachineDNAService:
    async def build_baseline(
        self,
        session: AsyncSession,
        machine_id: uuid.UUID,
    ):
        statement = (
            select(Telemetry)
            .where(
                Telemetry.machine_id == machine_id
            )
            .order_by(
                Telemetry.timestamp.asc()
            )
        )

        result = await session.execute(statement)
        measurements = list(result.scalars().all())

        if not measurements:
            raise ValueError(
                "No telemetry available for machine"
            )

        grouped: dict[
            datetime,
            dict[str, float],
        ] = defaultdict(dict)

        for measurement in measurements:
            grouped[measurement.timestamp][
                measurement.sensor
            ] = measurement.value

        sensor_names = sorted(
            {
                measurement.sensor
                for measurement in measurements
            }
        )

        complete_snapshots: list[
            tuple[datetime, dict[str, float]]
        ] = []

        for timestamp, values in grouped.items():
            if all(
                sensor in values
                for sensor in sensor_names
            ):
                complete_snapshots.append(
                    (
                        timestamp,
                        values,
                    )
                )

        if len(complete_snapshots) < 2:
            raise ValueError(
                "Not enough complete telemetry snapshots"
            )

        complete_snapshots.sort(
            key=lambda item: item[0]
        )

        sensor_series: dict[
            str,
            list[float],
        ] = {
            sensor: []
            for sensor in sensor_names
        }

        for _, values in complete_snapshots:
            for sensor in sensor_names:
                sensor_series[sensor].append(
                    values[sensor]
                )

        features = feature_engine.build(
            sensor_series
        )

        baseline_version = (
            await machine_baseline_repository.get_next_version(
                session,
                machine_id,
            )
        )

        baseline = await machine_baseline_repository.create(
            session,
            machine_id=machine_id,
            sample_count=len(
                complete_snapshots
            ),
            window_start=complete_snapshots[0][0],
            window_end=complete_snapshots[-1][0],
            sensor_features=features.sensors,
            correlations=features.correlations,
            baseline_version=baseline_version,
        )

        return baseline


machine_dna_service = MachineDNAService()
