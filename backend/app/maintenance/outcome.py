from dataclasses import dataclass
from enum import Enum
from statistics import mean


class LearnedOutcomeState(str, Enum):
    HIGHLY_EFFECTIVE = "highly_effective"
    EFFECTIVE = "effective"
    LIMITED_EFFECT = "limited_effect"
    INEFFECTIVE = "ineffective"
    NEGATIVE = "negative"


@dataclass(frozen=True)
class InterventionOutcome:
    recovery_score: float
    risk_reduction: float
    drift_reduction: float
    health_improvement: float


@dataclass(frozen=True)
class LearnedInterventionProfile:
    intervention_type: str
    sample_count: int
    average_recovery_score: float
    average_risk_reduction: float
    average_drift_reduction: float
    average_health_improvement: float
    success_rate: float
    confidence: float
    state: LearnedOutcomeState


class MaintenanceOutcomeLearningEngine:
    def classify(self, recovery_score: float) -> LearnedOutcomeState:
        score = float(recovery_score)
        if score >= 0.55:
            return LearnedOutcomeState.HIGHLY_EFFECTIVE
        if score >= 0.25:
            return LearnedOutcomeState.EFFECTIVE
        if score >= 0.08:
            return LearnedOutcomeState.LIMITED_EFFECT
        if score >= -0.08:
            return LearnedOutcomeState.INEFFECTIVE
        return LearnedOutcomeState.NEGATIVE

    def learn(
        self,
        *,
        intervention_type: str,
        outcomes: list[InterventionOutcome],
    ) -> LearnedInterventionProfile:
        if not outcomes:
            raise ValueError("at least one completed intervention outcome is required")

        avg_recovery = mean(x.recovery_score for x in outcomes)
        avg_risk = mean(x.risk_reduction for x in outcomes)
        avg_drift = mean(x.drift_reduction for x in outcomes)
        avg_health = mean(x.health_improvement for x in outcomes)

        successes = sum(1 for x in outcomes if x.recovery_score >= 0.25)
        success_rate = successes / len(outcomes)

        # Evidence confidence grows with repeated observations but stays conservative.
        confidence = min(1.0, len(outcomes) / 10.0)

        return LearnedInterventionProfile(
            intervention_type=intervention_type,
            sample_count=len(outcomes),
            average_recovery_score=round(avg_recovery, 4),
            average_risk_reduction=round(avg_risk, 4),
            average_drift_reduction=round(avg_drift, 4),
            average_health_improvement=round(avg_health, 4),
            success_rate=round(success_rate, 4),
            confidence=round(confidence, 4),
            state=self.classify(avg_recovery),
        )


maintenance_outcome_learning_engine = MaintenanceOutcomeLearningEngine()
