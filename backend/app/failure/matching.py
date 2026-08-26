from dataclasses import dataclass
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class FailureMatchScore:
    overall_similarity: float
    sensor_similarity: float
    deviation_similarity: float
    drift_similarity: float
    correlation_similarity: float
    trajectory_similarity: float


class FailureTrajectoryMatcher:
    SENSOR_WEIGHT = 0.30
    DEVIATION_WEIGHT = 0.15
    DRIFT_WEIGHT = 0.25
    CORRELATION_WEIGHT = 0.15
    TRAJECTORY_WEIGHT = 0.15

    def match(
        self,
        current: Any,
        historical: Any,
    ) -> FailureMatchScore:
        sensor_similarity = self._sensor_similarity(
            self._value(current, "dominant_sensors", []),
            self._value(historical, "dominant_sensors", []),
        )

        deviation_similarity = self._signature_similarity(
            self._value(current, "deviation_signature", {}),
            self._value(historical, "deviation_signature", {}),
            numeric_keys=(
                "max_score",
                "mean_score",
            ),
            categorical_keys=(
                "severities",
            ),
        )

        drift_similarity = self._drift_similarity(
            self._value(current, "drift_signature", {}),
            self._value(historical, "drift_signature", {}),
        )

        correlation_similarity = (
            self._correlation_similarity(
                self._value(
                    current,
                    "correlation_signature",
                    {},
                ),
                self._value(
                    historical,
                    "correlation_signature",
                    {},
                ),
            )
        )

        trajectory_similarity = (
            self._trajectory_similarity(
                self._value(
                    current,
                    "trajectory_summary",
                    {},
                ),
                self._value(
                    historical,
                    "trajectory_summary",
                    {},
                ),
            )
        )

        overall_similarity = (
            sensor_similarity * self.SENSOR_WEIGHT
            + deviation_similarity * self.DEVIATION_WEIGHT
            + drift_similarity * self.DRIFT_WEIGHT
            + correlation_similarity
            * self.CORRELATION_WEIGHT
            + trajectory_similarity
            * self.TRAJECTORY_WEIGHT
        )

        return FailureMatchScore(
            overall_similarity=self._clamp(
                overall_similarity
            ),
            sensor_similarity=self._clamp(
                sensor_similarity
            ),
            deviation_similarity=self._clamp(
                deviation_similarity
            ),
            drift_similarity=self._clamp(
                drift_similarity
            ),
            correlation_similarity=self._clamp(
                correlation_similarity
            ),
            trajectory_similarity=self._clamp(
                trajectory_similarity
            ),
        )

    def _sensor_similarity(
        self,
        current: list[dict],
        historical: list[dict],
    ) -> float:
        current_map = {
            str(item.get("sensor")): self._safe_float(
                item.get("mean_score")
                or item.get("max_score")
                or item.get("score")
            )
            for item in current
            if item.get("sensor")
        }

        historical_map = {
            str(item.get("sensor")): self._safe_float(
                item.get("mean_score")
                or item.get("max_score")
                or item.get("score")
            )
            for item in historical
            if item.get("sensor")
        }

        return self._weighted_map_similarity(
            current_map,
            historical_map,
        )

    def _drift_similarity(
        self,
        current: dict,
        historical: dict,
    ) -> float:
        base_similarity = self._signature_similarity(
            current,
            historical,
            numeric_keys=(
                "max_score",
                "mean_score",
            ),
            categorical_keys=(
                "states",
            ),
        )

        current_signals = {
            str(item.get("signal")): self._safe_float(
                item.get("mean_score")
                or item.get("max_score")
                or item.get("score")
            )
            for item in current.get(
                "dominant_signals",
                [],
            )
            if item.get("signal")
        }

        historical_signals = {
            str(item.get("signal")): self._safe_float(
                item.get("mean_score")
                or item.get("max_score")
                or item.get("score")
            )
            for item in historical.get(
                "dominant_signals",
                [],
            )
            if item.get("signal")
        }

        signal_similarity = (
            self._weighted_map_similarity(
                current_signals,
                historical_signals,
            )
        )

        if not current_signals and not historical_signals:
            return base_similarity

        return (
            base_similarity * 0.50
            + signal_similarity * 0.50
        )

    def _correlation_similarity(
        self,
        current: dict,
        historical: dict,
    ) -> float:
        current_map = {
            str(item.get("relationship")): self._safe_float(
                item.get("mean_delta")
                or item.get("max_delta")
                or item.get("delta")
            )
            for item in current.get(
                "relationships",
                [],
            )
            if item.get("relationship")
        }

        historical_map = {
            str(item.get("relationship")): self._safe_float(
                item.get("mean_delta")
                or item.get("max_delta")
                or item.get("delta")
            )
            for item in historical.get(
                "relationships",
                [],
            )
            if item.get("relationship")
        }

        return self._weighted_map_similarity(
            current_map,
            historical_map,
        )

    def _trajectory_similarity(
        self,
        current: dict,
        historical: dict,
    ) -> float:
        keys = (
            "max_deviation_score",
            "mean_deviation_score",
            "max_drift_score",
            "mean_drift_score",
        )

        similarities: list[float] = []

        for key in keys:
            if (
                current.get(key) is None
                or historical.get(key) is None
            ):
                continue

            similarities.append(
                self._numeric_similarity(
                    self._safe_float(
                        current.get(key)
                    ),
                    self._safe_float(
                        historical.get(key)
                    ),
                )
            )

        current_duration = current.get(
            "duration_seconds"
        )
        historical_duration = historical.get(
            "duration_seconds"
        )

        if (
            current_duration is not None
            and historical_duration is not None
        ):
            similarities.append(
                self._ratio_similarity(
                    self._safe_float(
                        current_duration
                    ),
                    self._safe_float(
                        historical_duration
                    ),
                )
            )

        if not similarities:
            return 0.0

        return sum(similarities) / len(similarities)

    def _signature_similarity(
        self,
        current: dict,
        historical: dict,
        *,
        numeric_keys: tuple[str, ...],
        categorical_keys: tuple[str, ...],
    ) -> float:
        similarities: list[float] = []

        for key in numeric_keys:
            if (
                current.get(key) is None
                or historical.get(key) is None
            ):
                continue

            similarities.append(
                self._numeric_similarity(
                    self._safe_float(
                        current.get(key)
                    ),
                    self._safe_float(
                        historical.get(key)
                    ),
                )
            )

        for key in categorical_keys:
            current_values = set(
                current.get(key) or []
            )
            historical_values = set(
                historical.get(key) or []
            )

            if not current_values and not historical_values:
                continue

            similarities.append(
                self._set_similarity(
                    current_values,
                    historical_values,
                )
            )

        if not similarities:
            return 0.0

        return sum(similarities) / len(similarities)

    def _weighted_map_similarity(
        self,
        current: dict[str, float],
        historical: dict[str, float],
    ) -> float:
        if not current or not historical:
            return 0.0

        current_keys = set(current)
        historical_keys = set(historical)

        overlap = current_keys & historical_keys
        union = current_keys | historical_keys

        if not union:
            return 0.0

        structural_similarity = (
            len(overlap) / len(union)
        )

        if not overlap:
            return 0.0

        value_similarity = sum(
            self._numeric_similarity(
                current[key],
                historical[key],
            )
            for key in overlap
        ) / len(overlap)

        return (
            structural_similarity * 0.50
            + value_similarity * 0.50
        )

    @staticmethod
    def _set_similarity(
        current: set,
        historical: set,
    ) -> float:
        union = current | historical

        if not union:
            return 1.0

        return len(
            current & historical
        ) / len(union)

    @staticmethod
    def _numeric_similarity(
        current: float,
        historical: float,
    ) -> float:
        difference = abs(
            current - historical
        )

        scale = max(
            abs(current),
            abs(historical),
            1.0,
        )

        return FailureTrajectoryMatcher._clamp(
            1.0 - difference / scale
        )

    @staticmethod
    def _ratio_similarity(
        current: float,
        historical: float,
    ) -> float:
        current = abs(current)
        historical = abs(historical)

        if current == 0.0 and historical == 0.0:
            return 1.0

        maximum = max(
            current,
            historical,
        )

        if maximum == 0.0:
            return 0.0

        return min(
            current,
            historical,
        ) / maximum

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> float:
        try:
            result = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        if not isfinite(result):
            return 0.0

        return result

    @staticmethod
    def _value(
        source: Any,
        name: str,
        default: Any,
    ) -> Any:
        if isinstance(source, dict):
            return source.get(
                name,
                default,
            )

        return getattr(
            source,
            name,
            default,
        )

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        return max(
            0.0,
            min(1.0, value),
        )


failure_trajectory_matcher = (
    FailureTrajectoryMatcher()
)

