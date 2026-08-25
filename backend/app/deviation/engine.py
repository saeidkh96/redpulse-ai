from dataclasses import asdict, dataclass

from app.deviation.scoring import (
    calculate_correlation_deviation,
    calculate_sensor_deviation,
)


@dataclass(frozen=True)
class DeviationReport:
    overall_score: float
    severity: str
    sensor_deviations: dict[str, dict]
    correlation_shifts: dict[str, dict]


class DeviationEngine:
    CRITICAL_ZSCORE = 5.0
    CRITICAL_SENSOR_COUNT = 2

    def compare(
        self,
        *,
        baseline_sensors: dict,
        baseline_correlations: dict[str, float],
        current_sensors: dict,
        current_correlations: dict[str, float],
    ) -> DeviationReport:
        sensor_deviations: dict[str, dict] = {}
        sensor_scores: list[float] = []

        for sensor, baseline_features in baseline_sensors.items():
            current_features = current_sensors.get(sensor)

            if current_features is None:
                continue

            result = calculate_sensor_deviation(
                baseline_mean=float(
                    baseline_features["mean"]
                ),
                baseline_std=float(
                    baseline_features["std"]
                ),
                current_mean=float(
                    current_features["mean"]
                ),
                current_std=float(
                    current_features["std"]
                ),
            )

            sensor_deviations[sensor] = asdict(result)
            sensor_scores.append(result.score)

        correlation_shifts: dict[str, dict] = {}
        correlation_scores: list[float] = []

        for key, baseline_value in baseline_correlations.items():
            if key not in current_correlations:
                continue

            result = calculate_correlation_deviation(
                baseline=float(baseline_value),
                current=float(
                    current_correlations[key]
                ),
            )

            correlation_shifts[key] = asdict(result)
            correlation_scores.append(result.score)

        sensor_score = (
            sum(sensor_scores) / len(sensor_scores)
            if sensor_scores
            else 0.0
        )

        correlation_score = (
            sum(correlation_scores)
            / len(correlation_scores)
            if correlation_scores
            else 0.0
        )

        overall_score = (
            sensor_score * 0.75
            + correlation_score * 0.25
        )

        overall_score = min(
            max(overall_score, 0.0),
            1.0,
        )

        severity = self._severity(
            overall_score,
            sensor_deviations,
        )

        return DeviationReport(
            overall_score=overall_score,
            severity=severity,
            sensor_deviations=sensor_deviations,
            correlation_shifts=correlation_shifts,
        )

    def _severity(
        self,
        score: float,
        sensor_deviations: dict[str, dict],
    ) -> str:
        critical_sensors = sum(
            1
            for deviation in sensor_deviations.values()
            if deviation["mean_zscore"]
            >= self.CRITICAL_ZSCORE
        )

        if (
            score >= 0.50
            or critical_sensors
            >= self.CRITICAL_SENSOR_COUNT
        ):
            return "anomalous"

        if score >= 0.20:
            return "warning"

        return "normal"


deviation_engine = DeviationEngine()
