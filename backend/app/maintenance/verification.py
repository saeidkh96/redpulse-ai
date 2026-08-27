from dataclasses import dataclass
from enum import Enum


class RecoveryState(str, Enum):
    RECOVERED = "recovered"
    PARTIALLY_RECOVERED = "partially_recovered"
    NO_IMPROVEMENT = "no_improvement"
    WORSENED = "worsened"


@dataclass(frozen=True)
class MaintenanceSnapshot:
    health_score: float
    risk_score: float
    deviation_score: float
    drift_score: float
    failure_match_score: float


@dataclass(frozen=True)
class MaintenanceVerification:
    recovery_score: float
    state: RecoveryState
    health_improvement: float
    risk_reduction: float
    deviation_reduction: float
    drift_reduction: float
    failure_match_reduction: float
    components: dict[str, float]


class MaintenanceVerificationEngine:
    HEALTH_WEIGHT = 0.30
    RISK_WEIGHT = 0.25
    DEVIATION_WEIGHT = 0.15
    DRIFT_WEIGHT = 0.15
    FAILURE_MATCH_WEIGHT = 0.15

    def verify(
        self,
        *,
        before: MaintenanceSnapshot,
        after: MaintenanceSnapshot,
    ) -> MaintenanceVerification:
        health_improvement = self._normalized_change(
            before.health_score,
            after.health_score,
            higher_is_better=True,
        )

        risk_reduction = self._normalized_change(
            before.risk_score,
            after.risk_score,
            higher_is_better=False,
        )

        deviation_reduction = self._normalized_change(
            before.deviation_score,
            after.deviation_score,
            higher_is_better=False,
        )

        drift_reduction = self._normalized_change(
            before.drift_score,
            after.drift_score,
            higher_is_better=False,
        )

        failure_match_reduction = self._normalized_change(
            before.failure_match_score,
            after.failure_match_score,
            higher_is_better=False,
        )

        components = {
            "health": (
                health_improvement
                * self.HEALTH_WEIGHT
            ),
            "risk": (
                risk_reduction
                * self.RISK_WEIGHT
            ),
            "deviation": (
                deviation_reduction
                * self.DEVIATION_WEIGHT
            ),
            "drift": (
                drift_reduction
                * self.DRIFT_WEIGHT
            ),
            "failure_match": (
                failure_match_reduction
                * self.FAILURE_MATCH_WEIGHT
            ),
        }

        recovery_score = self._clamp_signed(
            sum(components.values())
        )

        state = self._state(
            recovery_score
        )

        return MaintenanceVerification(
            recovery_score=round(recovery_score, 4),
            state=state,
            health_improvement=round(
                health_improvement,
                4,
            ),
            risk_reduction=round(
                risk_reduction,
                4,
            ),
            deviation_reduction=round(
                deviation_reduction,
                4,
            ),
            drift_reduction=round(
                drift_reduction,
                4,
            ),
            failure_match_reduction=round(
                failure_match_reduction,
                4,
            ),
            components={
                key: round(value, 4)
                for key, value in components.items()
            },
        )

    @staticmethod
    def _normalized_change(
        before: float,
        after: float,
        *,
        higher_is_better: bool,
    ) -> float:
        before = float(before)
        after = float(after)

        if higher_is_better:
            change = (after - before) / 100.0
        else:
            change = before - after

        return MaintenanceVerificationEngine._clamp_signed(
            change
        )

    @staticmethod
    def _state(
        recovery_score: float,
    ) -> RecoveryState:
        if recovery_score >= 0.35:
            return RecoveryState.RECOVERED

        if recovery_score >= 0.10:
            return RecoveryState.PARTIALLY_RECOVERED

        if recovery_score >= -0.10:
            return RecoveryState.NO_IMPROVEMENT

        return RecoveryState.WORSENED

    @staticmethod
    def _clamp_signed(
        value: float,
    ) -> float:
        return max(
            -1.0,
            min(
                1.0,
                float(value),
            ),
        )


maintenance_verification_engine = (
    MaintenanceVerificationEngine()
)
