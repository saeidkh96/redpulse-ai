from dataclasses import dataclass
from enum import Enum

from app.maintenance.outcome import LearnedInterventionProfile
from app.maintenance.verification import MaintenanceSnapshot


class CounterfactualEvidenceScope(str, Enum):
    MACHINE_TYPE = "machine_type"
    GLOBAL = "global"


@dataclass(frozen=True)
class CounterfactualOutcome:
    intervention_type: str
    predicted_health_score: float
    predicted_risk_score: float
    predicted_deviation_score: float
    predicted_drift_score: float
    predicted_failure_match_score: float
    expected_recovery_score: float
    avoided_risk: float
    avoided_health_loss: float
    avoided_drift: float
    estimated_intervention_benefit: float
    confidence: float
    historical_support: int
    evidence_scope: CounterfactualEvidenceScope


@dataclass(frozen=True)
class CounterfactualAnalysis:
    current: MaintenanceSnapshot
    no_maintenance: CounterfactualOutcome
    candidates: list[CounterfactualOutcome]
    recommended_intervention: str | None
    recommendation_confidence: float
    horizon_steps: int


class CounterfactualMaintenanceEngine:
    HEALTH_WEIGHT = 0.35
    RISK_WEIGHT = 0.30
    DRIFT_WEIGHT = 0.20
    RECOVERY_WEIGHT = 0.15

    def analyze(
        self,
        *,
        current: MaintenanceSnapshot,
        profiles: list[LearnedInterventionProfile],
        horizon_steps: int,
        evidence_scope: CounterfactualEvidenceScope,
    ) -> CounterfactualAnalysis:
        if horizon_steps < 1:
            raise ValueError("horizon_steps must be at least 1")

        no_maintenance = self._no_maintenance_outcome(
            current=current,
            horizon_steps=horizon_steps,
        )

        candidates = [
            self._candidate_outcome(
                current=current,
                no_maintenance=no_maintenance,
                profile=profile,
                evidence_scope=evidence_scope,
            )
            for profile in profiles
        ]
        candidates.sort(
            key=lambda item: (
                item.estimated_intervention_benefit,
                item.confidence,
                item.historical_support,
            ),
            reverse=True,
        )

        recommended = candidates[0] if candidates else None
        return CounterfactualAnalysis(
            current=current,
            no_maintenance=no_maintenance,
            candidates=candidates,
            recommended_intervention=(
                recommended.intervention_type if recommended is not None else None
            ),
            recommendation_confidence=(
                recommended.confidence if recommended is not None else 0.0
            ),
            horizon_steps=horizon_steps,
        )

    def _no_maintenance_outcome(
        self,
        *,
        current: MaintenanceSnapshot,
        horizon_steps: int,
    ) -> CounterfactualOutcome:
        horizon_factor = min(3.0, max(1.0, horizon_steps / 5.0))

        risk = self._clamp01(current.risk_score)
        deviation = self._clamp01(current.deviation_score)
        drift = self._clamp01(current.drift_score)
        failure_match = self._clamp01(current.failure_match_score)

        degradation_pressure = self._clamp01(
            (risk * 0.35)
            + (drift * 0.25)
            + (deviation * 0.20)
            + (failure_match * 0.20)
        )

        health_loss = min(
            max(0.0, current.health_score),
            (4.0 + (14.0 * degradation_pressure)) * horizon_factor,
        )
        predicted_health = self._clamp100(
            current.health_score - health_loss
        )

        predicted_risk = self._clamp01(
            risk + ((0.05 + (0.15 * degradation_pressure)) * horizon_factor)
        )
        predicted_deviation = self._clamp01(
            deviation + ((0.03 + (0.10 * degradation_pressure)) * horizon_factor)
        )
        predicted_drift = self._clamp01(
            drift + ((0.04 + (0.12 * degradation_pressure)) * horizon_factor)
        )
        predicted_failure_match = self._clamp01(
            failure_match + ((0.03 + (0.10 * degradation_pressure)) * horizon_factor)
        )

        baseline_confidence = self._clamp01(
            0.30
            + (0.20 * degradation_pressure)
            - (0.04 * max(0, horizon_steps - 5))
        )

        return CounterfactualOutcome(
            intervention_type="no_maintenance",
            predicted_health_score=round(predicted_health, 4),
            predicted_risk_score=round(predicted_risk, 4),
            predicted_deviation_score=round(predicted_deviation, 4),
            predicted_drift_score=round(predicted_drift, 4),
            predicted_failure_match_score=round(predicted_failure_match, 4),
            expected_recovery_score=0.0,
            avoided_risk=0.0,
            avoided_health_loss=0.0,
            avoided_drift=0.0,
            estimated_intervention_benefit=0.0,
            confidence=round(baseline_confidence, 4),
            historical_support=0,
            evidence_scope=CounterfactualEvidenceScope.GLOBAL,
        )

    def _candidate_outcome(
        self,
        *,
        current: MaintenanceSnapshot,
        no_maintenance: CounterfactualOutcome,
        profile: LearnedInterventionProfile,
        evidence_scope: CounterfactualEvidenceScope,
    ) -> CounterfactualOutcome:
        predicted_health = self._clamp100(
            no_maintenance.predicted_health_score
            + (profile.average_health_improvement * 100.0)
        )
        predicted_risk = self._clamp01(
            no_maintenance.predicted_risk_score
            - profile.average_risk_reduction
        )
        predicted_drift = self._clamp01(
            no_maintenance.predicted_drift_score
            - profile.average_drift_reduction
        )

        recovery = self._clamp_signed(profile.average_recovery_score)

        # v0.4.3 does not yet learn deviation/failure-match outcome averages.
        # Keep those values conservative rather than inventing unsupported gains.
        predicted_deviation = no_maintenance.predicted_deviation_score
        predicted_failure_match = no_maintenance.predicted_failure_match_score

        avoided_health_loss = max(
            0.0,
            predicted_health - no_maintenance.predicted_health_score,
        )
        avoided_risk = max(
            0.0,
            no_maintenance.predicted_risk_score - predicted_risk,
        )
        avoided_drift = max(
            0.0,
            no_maintenance.predicted_drift_score - predicted_drift,
        )

        normalized_health_gain = self._clamp01(avoided_health_loss / 100.0)
        positive_recovery = max(0.0, recovery)

        raw_benefit = self._clamp01(
            (normalized_health_gain * self.HEALTH_WEIGHT)
            + (avoided_risk * self.RISK_WEIGHT)
            + (avoided_drift * self.DRIFT_WEIGHT)
            + (positive_recovery * self.RECOVERY_WEIGHT)
        )

        evidence_confidence = self._clamp01(profile.confidence)
        scope_factor = (
            1.0
            if evidence_scope is CounterfactualEvidenceScope.MACHINE_TYPE
            else 0.85
        )
        ranking_confidence = self._clamp01(
            evidence_confidence
            * scope_factor
            * (0.50 + (0.50 * profile.success_rate))
        )

        evidence_adjusted_benefit = self._clamp01(
            raw_benefit * (0.50 + (0.50 * ranking_confidence))
        )

        return CounterfactualOutcome(
            intervention_type=profile.intervention_type,
            predicted_health_score=round(predicted_health, 4),
            predicted_risk_score=round(predicted_risk, 4),
            predicted_deviation_score=round(predicted_deviation, 4),
            predicted_drift_score=round(predicted_drift, 4),
            predicted_failure_match_score=round(predicted_failure_match, 4),
            expected_recovery_score=round(recovery, 4),
            avoided_risk=round(avoided_risk, 4),
            avoided_health_loss=round(avoided_health_loss, 4),
            avoided_drift=round(avoided_drift, 4),
            estimated_intervention_benefit=round(
                evidence_adjusted_benefit,
                4,
            ),
            confidence=round(ranking_confidence, 4),
            historical_support=profile.sample_count,
            evidence_scope=evidence_scope,
        )

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _clamp100(value: float) -> float:
        return max(0.0, min(100.0, float(value)))

    @staticmethod
    def _clamp_signed(value: float) -> float:
        return max(-1.0, min(1.0, float(value)))


counterfactual_maintenance_engine = CounterfactualMaintenanceEngine()
