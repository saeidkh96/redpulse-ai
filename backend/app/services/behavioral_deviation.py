import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.deviation.engine import (
    DeviationReport,
    deviation_engine,
)
from app.features.engine import feature_engine
from app.repositories.machine_baseline import (
    machine_baseline_repository,
)
from app.repositories.telemetry import telemetry_repository


class BehavioralDeviationError(Exception):
    pass


class BaselineNotFoundError(
    BehavioralDeviationError
):
    pass


class InsufficientTelemetryError(
    BehavioralDeviationError
):
    pass


@dataclass(frozen=True)
class BehavioralDeviationResult:
    baseline_version: str
    sample_count: int
    window_start: datetime
    window_end: datetime
    report: DeviationReport


class BehavioralDeviationService:
    MINIMUM_SAMPLES = 30
    ANALYSIS_WINDOW_SIZE = 100

    async def analyze(
        self,
        session: AsyncSession,
        machine_id: uuid.UUID,
    ) -> BehavioralDeviationResult:
        baseline = (
            await machine_baseline_repository.get_latest(
                session,
                machine_id,
            )
        )

        if baseline is None:
            raise BaselineNotFoundError(
                "Machine DNA baseline not found"
            )

        measurements = (
            await telemetry_repository.list_for_machine(
                session,
                machine_id=machine_id,
                start=baseline.window_end,
                limit=5000,
            )
        )

        measurements = [
            measurement
            for measurement in measurements
            if measurement.timestamp > baseline.window_end
        ]

        if not measurements:
            raise InsufficientTelemetryError(
                "Insufficient telemetry after baseline"
            )

        grouped: dict[
            datetime,
            dict[str, float],
        ] = defaultdict(dict)

        for measurement in measurements:
            grouped[measurement.timestamp][
                measurement.sensor
            ] = measurement.value

        baseline_sensor_names = sorted(
            baseline.sensor_features.keys()
        )

        complete_snapshots: list[
            tuple[datetime, dict[str, float]]
        ] = []

        for timestamp, values in grouped.items():
            if all(
                sensor in values
                for sensor in baseline_sensor_names
            ):
                complete_snapshots.append(
                    (
                        timestamp,
                        values,
                    )
                )

        complete_snapshots.sort(
            key=lambda item: item[0]
        )

        if len(complete_snapshots) < self.MINIMUM_SAMPLES:
            raise InsufficientTelemetryError(
                (
                    "Insufficient telemetry after baseline: "
                    f"{len(complete_snapshots)} complete snapshots "
                    f"available, {self.MINIMUM_SAMPLES} required"
                )
            )

        complete_snapshots = complete_snapshots[
            -self.ANALYSIS_WINDOW_SIZE:
        ]

        sensor_series: dict[
            str,
            list[float],
        ] = {
            sensor: []
            for sensor in baseline_sensor_names
        }

        for _, values in complete_snapshots:
            for sensor in baseline_sensor_names:
                sensor_series[sensor].append(
                    values[sensor]
                )

        current_features = feature_engine.build(
            sensor_series
        )

        report = deviation_engine.compare(
            baseline_sensors=baseline.sensor_features,
            baseline_correlations=baseline.correlations,
            current_sensors=current_features.sensors,
            current_correlations=current_features.correlations,
        )

        return BehavioralDeviationResult(
            baseline_version=baseline.baseline_version,
            sample_count=len(complete_snapshots),
            window_start=complete_snapshots[0][0],
            window_end=complete_snapshots[-1][0],
            report=report,
        )


behavioral_deviation_service = (
    BehavioralDeviationService()
)
