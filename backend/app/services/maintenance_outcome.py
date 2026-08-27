import uuid
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.maintenance.outcome import (
    InterventionOutcome,
    LearnedInterventionProfile,
    maintenance_outcome_learning_engine,
)
from app.repositories.maintenance_intervention import maintenance_intervention_repository


class MaintenanceOutcomeService:
    async def learn(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID | None = None,
        machine_type: str | None = None,
        intervention_type: str | None = None,
        limit: int = 1000,
    ) -> list[LearnedInterventionProfile]:
        records = await maintenance_intervention_repository.list_completed(
            session,
            machine_id=machine_id,
            machine_type=machine_type,
            intervention_type=intervention_type,
            limit=limit,
        )

        grouped: dict[str, list[InterventionOutcome]] = defaultdict(list)
        for record in records:
            verification = record.verification_result or {}
            if "recovery_score" not in verification:
                continue
            grouped[record.intervention_type].append(
                InterventionOutcome(
                    recovery_score=float(verification.get("recovery_score", 0.0)),
                    risk_reduction=float(verification.get("risk_reduction", 0.0)),
                    drift_reduction=float(verification.get("drift_reduction", 0.0)),
                    health_improvement=float(verification.get("health_improvement", 0.0)),
                )
            )

        profiles = [
            maintenance_outcome_learning_engine.learn(
                intervention_type=kind,
                outcomes=outcomes,
            )
            for kind, outcomes in grouped.items()
        ]
        profiles.sort(
            key=lambda x: (x.average_recovery_score, x.confidence),
            reverse=True,
        )
        return profiles


maintenance_outcome_service = MaintenanceOutcomeService()
