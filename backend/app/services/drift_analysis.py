import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.deviation.engine import deviation_engine
from app.drift.detector import DriftReport, drift_detector
from app.features.engine import feature_engine
from app.repositories.machine_baseline import (
    machine_baseline_repository,
)
from app.repositories.telemetry import telemetry_repository


class DriftAnalysisError(Exception):
    pass


class DriftBaselineNotFoundError(
    DriftAnalysisError
):
    pass


class DriftTelemetryError(
    DriftAnalysisError
):
    pass


@dataclass(frozen=True)
class DriftWindow:
    index: int
    window_start: datetime
    window_end: datetime
    sample_count: int
    deviation_score: float
    severity: str


@dataclass(frozen=True)
class DriftAnalysisResult:
    baseline_version: str
    window_size: int
    window_count: int
    windows: list[DriftWindow]
    drift_report: DriftReport


class DriftAnalysisService:
    WINDOW_SIZE = 50
    MINIMUM_WINDOWS = 3
    MAX_WINDOWS = 10

    async def analyze(
        self,
        session: AsyncSession,
        machine_id: uuid.UUID,
    ) -> DriftAnalysisResult:
        baseline = (
            await machine_baseline_repository.get_latest(
                session,
                machine_id,
            )
        )

        if baseline is None:
            raise DriftBaselineNotFoundError(
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

        minimum_samples = (
            self.WINDOW_SIZE
            * self.MINIMUM_WINDOWS
        )

        if len(complete_snapshots) < minimum_samples:
            raise DriftTelemetryError(
                (
                    "Insufficient telemetry for drift analysis: "
                    f"{len(complete_snapshots)} complete snapshots "
                    f"available, {minimum_samples} required"
                )
            )

        maximum_samples = (
            self.WINDOW_SIZE
            * self.MAX_WINDOWS
        )

        complete_snapshots = complete_snapshots[
            -maximum_samples:
        ]

        windows: list[DriftWindow] = []

        signal_history: dict[
            str,
            list[float],
        ] = {
            "overall_deviation": [],
        }

        for start_index in range(
            0,
            len(complete_snapshots),
            self.WINDOW_SIZE,
        ):
            chunk = complete_snapshots[
                start_index:
                start_index + self.WINDOW_SIZE
            ]

            if len(chunk) < self.WINDOW_SIZE:
                continue

            sensor_series: dict[
                str,
                list[float],
            ] = {
                sensor: []
                for sensor in baseline_sensor_names
            }

            for _, values in chunk:
                for sensor in baseline_sensor_names:
                    sensor_series[sensor].append(
                        values[sensor]
                    )

            current_features = (
                feature_engine.build(
                    sensor_series
                )
            )

            deviation = deviation_engine.compare(
                baseline_sensors=baseline.sensor_features,
                baseline_correlations=baseline.correlations,
                current_sensors=current_features.sensors,
                current_correlations=current_features.correlations,
            )

            window = DriftWindow(
                index=len(windows),
                window_start=chunk[0][0],
                window_end=chunk[-1][0],
                sample_count=len(chunk),
                deviation_score=deviation.overall_score,
                severity=deviation.severity,
            )

            windows.append(window)

            signal_history[
                "overall_deviation"
            ].append(
                deviation.overall_score
            )

            for sensor, deviation_data in (
                deviation.sensor_deviations.items()
            ):
                key = f"{sensor}__mean_zscore"

                signal_history.setdefault(
                    key,
                    [],
                ).append(
                    float(
                        deviation_data[
                            "mean_zscore"
                        ]
                    )
                )

        if len(windows) < self.MINIMUM_WINDOWS:
            raise DriftTelemetryError(
                (
                    "Insufficient complete windows for "
                    "drift analysis"
                )
            )

        drift_report = drift_detector.analyze(
            signal_history
        )

        return DriftAnalysisResult(
            baseline_version=baseline.baseline_version,
            window_size=self.WINDOW_SIZE,
            window_count=len(windows),
            windows=windows,
            drift_report=drift_report,
        )


drift_analysis_service = DriftAnalysisService()
