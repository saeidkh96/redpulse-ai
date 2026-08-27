import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.maintenance.decision import (
    MaintenanceDecision,
    MaintenanceDecisionInput,
    maintenance_decision_engine,
)
from app.services.failure_explanation import (
    FailureExplanationResult,
    failure_explanation_service,
)


@dataclass(frozen=True)
class MaintenanceRecommendationResult:
    machine_id: uuid.UUID
    explanation_result: FailureExplanationResult
    decision: MaintenanceDecision


class MaintenanceRecommendationService:
    async def recommend(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        machine_type: str | None = None,
        event_limit: int = 100,
        library_limit: int = 500,
    ) -> MaintenanceRecommendationResult:
        if event_limit < 1:
            raise ValueError(
                "event_limit must be at least 1"
            )

        if library_limit < 1:
            raise ValueError(
                "library_limit must be at least 1"
            )

        explanation_result = (
            await failure_explanation_service.explain(
                session,
                machine_id=machine_id,
                machine_type=machine_type,
                event_limit=event_limit,
                library_limit=library_limit,
            )
        )

        decision = maintenance_decision_engine.decide(
            MaintenanceDecisionInput(
                prediction=(
                    explanation_result.prediction
                ),
                explanation=(
                    explanation_result.explanation
                ),
            )
        )

        return MaintenanceRecommendationResult(
            machine_id=machine_id,
            explanation_result=explanation_result,
            decision=decision,
        )


maintenance_recommendation_service = (
    MaintenanceRecommendationService()
)
