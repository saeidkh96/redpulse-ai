import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.explainability.failure_explanation import (
    FailureExplanation,
    failure_explanation_engine,
)
from app.failure.fingerprint import (
    FailureFingerprintData,
    failure_fingerprint_builder,
)
from app.models.behavior_event import (
    BehaviorEventType,
)
from app.repositories.behavior_event import (
    behavior_event_repository,
)
from app.services.failure_prediction import (
    FailurePredictionResult,
    failure_prediction_service,
)


@dataclass(frozen=True)
class FailureExplanationResult:
    machine_id: uuid.UUID
    prediction: FailurePredictionResult
    current_fingerprint: FailureFingerprintData | None
    explanation: FailureExplanation


class FailureExplanationService:
    async def explain(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        machine_type: str | None = None,
        event_limit: int = 100,
        library_limit: int = 500,
    ) -> FailureExplanationResult:
        if event_limit < 1:
            raise ValueError(
                "event_limit must be at least 1"
            )

        if library_limit < 1:
            raise ValueError(
                "library_limit must be at least 1"
            )

        prediction = (
            await failure_prediction_service.predict(
                session,
                machine_id=machine_id,
                machine_type=machine_type,
                event_limit=event_limit,
                library_limit=library_limit,
            )
        )

        events = (
            await behavior_event_repository.list_for_machine(
                session,
                machine_id,
                limit=event_limit,
            )
        )

        relevant_events = [
            event
            for event in events
            if event.event_type
            in {
                BehaviorEventType.DEVIATION,
                BehaviorEventType.DRIFT,
            }
        ]

        current_fingerprint = None

        if relevant_events:
            current_fingerprint = (
                failure_fingerprint_builder.build(
                    relevant_events
                )
            )

        explanation = (
            failure_explanation_engine.explain(
                prediction_evidence=(
                    prediction.evidence
                ),
                risk_components=(
                    prediction.risk.components
                ),
                dominant_sensors=(
                    current_fingerprint.dominant_sensors
                    if current_fingerprint
                    else []
                ),
                drift_signature=(
                    current_fingerprint.drift_signature
                    if current_fingerprint
                    else {}
                ),
                correlation_signature=(
                    current_fingerprint
                    .correlation_signature
                    if current_fingerprint
                    else {}
                ),
                trajectory_summary=(
                    current_fingerprint
                    .trajectory_summary
                    if current_fingerprint
                    else {}
                ),
            )
        )

        return FailureExplanationResult(
            machine_id=machine_id,
            prediction=prediction,
            current_fingerprint=(
                current_fingerprint
            ),
            explanation=explanation,
        )


failure_explanation_service = (
    FailureExplanationService()
)
