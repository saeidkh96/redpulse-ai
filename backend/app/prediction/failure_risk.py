from dataclasses import dataclass
from enum import Enum


class FailureRiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class FailureTrend(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    WORSENING = "worsening"


@dataclass(frozen=True)
class FailureRiskInput:
    health_risk_score: float
    failure_match_score: float
    persistence_score: float
    deviation_score: float
    drift_score: float


@dataclass(frozen=True)
class FailureRiskResult:
    risk_score: float
    confidence: float
    level: FailureRiskLevel
    trend: FailureTrend
    components: dict[str, float]


class FailureRiskScorer:
    HEALTH_WEIGHT = 0.30
    FAILURE_MATCH_WEIGHT = 0.35
    PERSISTENCE_WEIGHT = 0.15
    DEVIATION_WEIGHT = 0.08
    DRIFT_WEIGHT = 0.12

    def score(
        self,
        value: FailureRiskInput,
    ) -> FailureRiskResult:
        health = self._clamp(
            value.health_risk_score
        )
        failure_match = self._clamp(
            value.failure_match_score
        )
        persistence = self._clamp(
            value.persistence_score
        )
        deviation = self._clamp(
            value.deviation_score
        )
        drift = self._clamp(
            value.drift_score
        )

        components = {
            "health": (
                health
                * self.HEALTH_WEIGHT
            ),
            "failure_match": (
                failure_match
                * self.FAILURE_MATCH_WEIGHT
            ),
            "persistence": (
                persistence
                * self.PERSISTENCE_WEIGHT
            ),
            "deviation": (
                deviation
                * self.DEVIATION_WEIGHT
            ),
            "drift": (
                drift
                * self.DRIFT_WEIGHT
            ),
        }

        risk_score = self._clamp(
            sum(components.values())
        )

        confidence = self._confidence(
            failure_match=failure_match,
            persistence=persistence,
            deviation=deviation,
            drift=drift,
        )

        level = self._level(
            risk_score
        )

        trend = self._trend(
            deviation=deviation,
            drift=drift,
            persistence=persistence,
        )

        return FailureRiskResult(
            risk_score=round(
                risk_score,
                4,
            ),
            confidence=round(
                confidence,
                4,
            ),
            level=level,
            trend=trend,
            components={
                key: round(component, 4)
                for key, component
                in components.items()
            },
        )

    @staticmethod
    def _confidence(
        *,
        failure_match: float,
        persistence: float,
        deviation: float,
        drift: float,
    ) -> float:
        evidence_strength = (
            failure_match * 0.45
            + persistence * 0.25
            + deviation * 0.10
            + drift * 0.20
        )

        return max(
            0.0,
            min(
                1.0,
                evidence_strength,
            ),
        )

    @staticmethod
    def _level(
        risk_score: float,
    ) -> FailureRiskLevel:
        if risk_score >= 0.75:
            return FailureRiskLevel.CRITICAL

        if risk_score >= 0.55:
            return FailureRiskLevel.HIGH

        if risk_score >= 0.30:
            return FailureRiskLevel.MODERATE

        return FailureRiskLevel.LOW

    @staticmethod
    def _trend(
        *,
        deviation: float,
        drift: float,
        persistence: float,
    ) -> FailureTrend:
        trend_score = (
            drift * 0.50
            + persistence * 0.30
            + deviation * 0.20
        )

        if trend_score >= 0.55:
            return FailureTrend.WORSENING

        if trend_score <= 0.20:
            return FailureTrend.IMPROVING

        return FailureTrend.STABLE

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )


failure_risk_scorer = FailureRiskScorer()
