from dataclasses import dataclass
from enum import Enum


class MachineHealthState(str, Enum):
    HEALTHY = "healthy"
    WATCH = "watch"
    DEGRADED = "degraded"
    CRITICAL = "critical"


@dataclass(frozen=True)
class HealthScoreInput:
    deviation_score: float
    drift_score: float
    failure_match_score: float
    persistence_score: float


@dataclass(frozen=True)
class HealthScoreResult:
    health_score: float
    risk_score: float
    state: MachineHealthState
    early_warning: bool
    components: dict[str, float]


class MachineHealthScorer:
    DEVIATION_WEIGHT = 0.25
    DRIFT_WEIGHT = 0.30
    FAILURE_MATCH_WEIGHT = 0.35
    PERSISTENCE_WEIGHT = 0.10

    EARLY_WARNING_THRESHOLD = 0.40

    def score(
        self,
        value: HealthScoreInput,
    ) -> HealthScoreResult:
        deviation = self._clamp(
            value.deviation_score
        )
        drift = self._clamp(
            value.drift_score
        )
        failure_match = self._clamp(
            value.failure_match_score
        )
        persistence = self._clamp(
            value.persistence_score
        )

        components = {
            "deviation": (
                deviation
                * self.DEVIATION_WEIGHT
            ),
            "drift": (
                drift
                * self.DRIFT_WEIGHT
            ),
            "failure_match": (
                failure_match
                * self.FAILURE_MATCH_WEIGHT
            ),
            "persistence": (
                persistence
                * self.PERSISTENCE_WEIGHT
            ),
        }

        risk_score = self._clamp(
            sum(components.values())
        )

        health_score = (
            1.0 - risk_score
        ) * 100.0

        health_score = round(
            health_score,
            2,
        )

        risk_score = round(
            risk_score,
            4,
        )

        state = self._state(
            health_score
        )

        return HealthScoreResult(
            health_score=health_score,
            risk_score=risk_score,
            state=state,
            early_warning=(
                risk_score
                >= self.EARLY_WARNING_THRESHOLD
            ),
            components={
                key: round(component, 4)
                for key, component
                in components.items()
            },
        )

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        return max(
            0.0,
            min(1.0, float(value)),
        )

    @staticmethod
    def _state(
        health_score: float,
    ) -> MachineHealthState:
        if health_score >= 80.0:
            return MachineHealthState.HEALTHY

        if health_score >= 60.0:
            return MachineHealthState.WATCH

        if health_score >= 35.0:
            return MachineHealthState.DEGRADED

        return MachineHealthState.CRITICAL


machine_health_scorer = MachineHealthScorer()
