from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import mean


@dataclass(frozen=True)
class MonitoringSnapshot:
    sample_count: int
    prediction_mean: float
    prediction_std: float
    feature_drift_score: float
    prediction_drift_score: float
    quality_score: float
    state: str


class ModelMonitoringEngine:
    def analyze(
        self,
        *,
        reference_predictions: list[float],
        current_predictions: list[float],
        reference_features: dict[str, list[float]] | None = None,
        current_features: dict[str, list[float]] | None = None,
    ) -> MonitoringSnapshot:
        if not current_predictions:
            raise ValueError("current_predictions must not be empty")
        if not reference_predictions:
            raise ValueError("reference_predictions must not be empty")

        pred_mean = mean(current_predictions)
        pred_std = self._std(current_predictions)
        ref_mean = mean(reference_predictions)
        ref_std = max(self._std(reference_predictions), 1e-9)

        prediction_drift = min(1.0, abs(pred_mean - ref_mean) / (3.0 * ref_std))
        feature_drift = self._feature_drift(reference_features or {}, current_features or {})

        quality = max(0.0, 1.0 - (prediction_drift * 0.55 + feature_drift * 0.45))
        state = self._state(prediction_drift, feature_drift, quality)

        return MonitoringSnapshot(
            sample_count=len(current_predictions),
            prediction_mean=round(pred_mean, 6),
            prediction_std=round(pred_std, 6),
            feature_drift_score=round(feature_drift, 4),
            prediction_drift_score=round(prediction_drift, 4),
            quality_score=round(quality, 4),
            state=state,
        )

    def _feature_drift(self, reference: dict[str, list[float]], current: dict[str, list[float]]) -> float:
        shared = set(reference) & set(current)
        if not shared:
            return 0.0
        scores = []
        for name in shared:
            if not reference[name] or not current[name]:
                continue
            ref_mean = mean(reference[name])
            ref_std = max(self._std(reference[name]), 1e-9)
            cur_mean = mean(current[name])
            scores.append(min(1.0, abs(cur_mean - ref_mean) / (3.0 * ref_std)))
        return mean(scores) if scores else 0.0

    @staticmethod
    def _std(values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        m = mean(values)
        return sqrt(sum((x - m) ** 2 for x in values) / len(values))

    @staticmethod
    def _state(prediction_drift: float, feature_drift: float, quality: float) -> str:
        pressure = max(prediction_drift, feature_drift)
        if pressure >= 0.75 or quality <= 0.35:
            return "critical"
        if pressure >= 0.50 or quality <= 0.55:
            return "degraded"
        if pressure >= 0.25 or quality <= 0.75:
            return "watch"
        return "healthy"
