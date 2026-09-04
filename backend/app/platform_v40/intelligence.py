from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from app.platform_v38.failure_intelligence import FailureEstimator


@dataclass(frozen=True)
class IntelligenceInput:
    machine_id: str
    baseline: tuple[float, ...]
    current: tuple[float, ...]
    drift_score: float
    trajectory_match: float
    uncertainty: float = 0.1


@dataclass(frozen=True)
class IntelligenceDecision:
    machine_id: str
    deviation_score: float
    drift_score: float
    failure_risk: float
    health_score: float
    horizon_hours: float | None
    confidence: float
    evidence: tuple[str, ...]
    maintenance_priority: str


class PredictiveMaintenanceEngine:
    def __init__(self) -> None:
        self.failure = FailureEstimator()

    @staticmethod
    def deviation(baseline: tuple[float, ...], current: tuple[float, ...]) -> float:
        if len(baseline) != len(current) or not baseline:
            raise ValueError("baseline and current vectors must have equal non-zero dimensions")
        distance = sqrt(sum((a - b) ** 2 for a, b in zip(baseline, current))) / sqrt(len(baseline))
        return max(0.0, min(1.0, distance))

    def evaluate(self, value: IntelligenceInput) -> IntelligenceDecision:
        deviation = self.deviation(value.baseline, value.current)
        estimate = self.failure.estimate(deviation, value.drift_score, value.trajectory_match, value.uncertainty)
        health = max(0.0, min(100.0, 100.0 * (1.0 - estimate.risk)))
        priority = "critical" if estimate.risk >= 0.8 else "high" if estimate.risk >= 0.6 else "monitor"
        return IntelligenceDecision(
            value.machine_id,
            deviation,
            value.drift_score,
            estimate.risk,
            health,
            estimate.horizon_hours,
            estimate.confidence,
            estimate.evidence,
            priority,
        )
