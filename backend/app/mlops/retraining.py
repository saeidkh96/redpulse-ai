from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrainingContext:
    feature_drift_score: float
    prediction_drift_score: float
    quality_score: float
    new_failure_samples: int
    days_since_training: int


@dataclass(frozen=True)
class RetrainingDecision:
    should_retrain: bool
    urgency: str
    score: float
    reason_codes: list[str]


class RetrainingPolicyEngine:
    def decide(self, context: RetrainingContext) -> RetrainingDecision:
        sample_pressure = min(1.0, max(0, context.new_failure_samples) / 100.0)
        age_pressure = min(1.0, max(0, context.days_since_training) / 90.0)
        quality_pressure = max(0.0, 1.0 - context.quality_score)

        score = (
            context.feature_drift_score * 0.25
            + context.prediction_drift_score * 0.25
            + quality_pressure * 0.20
            + sample_pressure * 0.20
            + age_pressure * 0.10
        )
        score = max(0.0, min(1.0, score))

        reasons = []
        if context.feature_drift_score >= 0.5:
            reasons.append("FEATURE_DRIFT")
        if context.prediction_drift_score >= 0.5:
            reasons.append("PREDICTION_DRIFT")
        if context.quality_score <= 0.6:
            reasons.append("QUALITY_DEGRADATION")
        if context.new_failure_samples >= 50:
            reasons.append("NEW_FAILURE_EVIDENCE")
        if context.days_since_training >= 60:
            reasons.append("MODEL_AGE")

        return RetrainingDecision(
            should_retrain=score >= 0.45,
            urgency=self._urgency(score),
            score=round(score, 4),
            reason_codes=reasons or ["NO_RETRAINING_TRIGGER"],
        )

    @staticmethod
    def _urgency(score: float) -> str:
        if score >= 0.75:
            return "critical"
        if score >= 0.60:
            return "high"
        if score >= 0.45:
            return "medium"
        return "low"
