import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.prediction.failure_risk import (
    FailureRiskInput,
    FailureRiskResult,
    failure_risk_scorer,
)
from app.services.failure_matching import FailureMatch
from app.services.machine_health import (
    MachineHealthResult,
    machine_health_service,
)


@dataclass(frozen=True)
class FailurePredictionResult:
    machine_id: uuid.UUID
    likely_failure_type: str | None
    likely_failure_title: str | None
    risk: FailureRiskResult
    historical_match_confidence: float | None
    failure_match_score: float
    evidence: dict


class FailurePredictionService:
    async def predict(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        machine_type: str | None = None,
        event_limit: int = 100,
        library_limit: int = 500,
    ) -> FailurePredictionResult:
        health_result = (
            await machine_health_service.assess(
                session,
                machine_id=machine_id,
                machine_type=machine_type,
                event_limit=event_limit,
                library_limit=library_limit,
            )
        )

        risk = failure_risk_scorer.score(
            FailureRiskInput(
                health_risk_score=(
                    health_result.health.risk_score
                ),
                failure_match_score=(
                    health_result.failure_match_score
                ),
                persistence_score=(
                    health_result.persistence.score
                ),
                deviation_score=(
                    health_result.deviation_score
                ),
                drift_score=(
                    health_result.drift_score
                ),
            )
        )

        best_match = (
            health_result.best_failure_match
        )

        likely_failure_type = None
        likely_failure_title = None
        historical_match_confidence = None

        if best_match is not None:
            fingerprint = best_match.fingerprint

            likely_failure_type = (
                fingerprint.failure_type
            )

            likely_failure_title = (
                fingerprint.title
            )

            historical_match_confidence = (
                fingerprint.confidence
            )

        evidence = self._evidence(
            health_result=health_result,
            best_match=best_match,
        )

        return FailurePredictionResult(
            machine_id=machine_id,
            likely_failure_type=(
                likely_failure_type
            ),
            likely_failure_title=(
                likely_failure_title
            ),
            risk=risk,
            historical_match_confidence=(
                historical_match_confidence
            ),
            failure_match_score=(
                health_result.failure_match_score
            ),
            evidence=evidence,
        )

    @staticmethod
    def _evidence(
        *,
        health_result: MachineHealthResult,
        best_match: FailureMatch | None,
    ) -> dict:
        evidence = {
            "machine_health_score": (
                health_result.health.health_score
            ),
            "machine_health_state": (
                health_result.health.state.value
            ),
            "machine_risk_score": (
                health_result.health.risk_score
            ),
            "deviation_score": (
                health_result.deviation_score
            ),
            "drift_score": (
                health_result.drift_score
            ),
            "persistence_score": (
                health_result.persistence.score
            ),
            "persistence_event_count": (
                health_result.persistence.event_count
            ),
        }

        if best_match is not None:
            evidence["historical_failure"] = {
                "fingerprint_id": str(
                    best_match.fingerprint.id
                ),
                "failure_type": (
                    best_match
                    .fingerprint
                    .failure_type
                ),
                "similarity": (
                    best_match
                    .score
                    .overall_similarity
                ),
                "sensor_similarity": (
                    best_match
                    .score
                    .sensor_similarity
                ),
                "deviation_similarity": (
                    best_match
                    .score
                    .deviation_similarity
                ),
                "drift_similarity": (
                    best_match
                    .score
                    .drift_similarity
                ),
                "correlation_similarity": (
                    best_match
                    .score
                    .correlation_similarity
                ),
                "trajectory_similarity": (
                    best_match
                    .score
                    .trajectory_similarity
                ),
            }

        return evidence


failure_prediction_service = (
    FailurePredictionService()
)
