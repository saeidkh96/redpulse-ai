import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.maintenance.counterfactual import (
    CounterfactualAnalysis,
    CounterfactualEvidenceScope,
    counterfactual_maintenance_engine,
)
from app.maintenance.outcome import LearnedInterventionProfile
from app.maintenance.verification import MaintenanceSnapshot
from app.services.machine_health import machine_health_service
from app.services.maintenance_outcome import maintenance_outcome_service


@dataclass(frozen=True)
class CounterfactualMaintenanceResult:
    machine_id: uuid.UUID
    analysis: CounterfactualAnalysis
    evidence_note: str


class CounterfactualMaintenanceService:
    async def analyze(
        self,
        session: AsyncSession,
        *,
        machine_id: uuid.UUID,
        machine_type: str | None = None,
        candidate_interventions: list[str] | None = None,
        horizon_steps: int = 5,
        event_limit: int = 100,
        library_limit: int = 500,
        history_limit: int = 1000,
    ) -> CounterfactualMaintenanceResult:
        if horizon_steps < 1:
            raise ValueError("horizon_steps must be at least 1")

        health_result = await machine_health_service.assess(
            session,
            machine_id=machine_id,
            machine_type=machine_type,
            event_limit=event_limit,
            library_limit=library_limit,
        )

        current = MaintenanceSnapshot(
            health_score=health_result.health.health_score,
            risk_score=health_result.health.risk_score,
            deviation_score=health_result.deviation_score,
            drift_score=health_result.drift_score,
            failure_match_score=health_result.failure_match_score,
        )

        profiles, evidence_scope = await self._load_profiles(
            session,
            machine_type=machine_type,
            history_limit=history_limit,
        )

        if candidate_interventions:
            allowed = {
                item.strip()
                for item in candidate_interventions
                if item.strip()
            }
            profiles = [
                profile
                for profile in profiles
                if profile.intervention_type in allowed
            ]

        analysis = counterfactual_maintenance_engine.analyze(
            current=current,
            profiles=profiles,
            horizon_steps=horizon_steps,
            evidence_scope=evidence_scope,
        )

        evidence_note = (
            "Estimated counterfactual outcomes are evidence-based projections, "
            "not guaranteed future states. Intervention estimates use completed "
            "maintenance history; the no-maintenance trajectory is a conservative "
            "heuristic based on the current machine condition."
        )

        return CounterfactualMaintenanceResult(
            machine_id=machine_id,
            analysis=analysis,
            evidence_note=evidence_note,
        )

    async def _load_profiles(
        self,
        session: AsyncSession,
        *,
        machine_type: str | None,
        history_limit: int,
    ) -> tuple[
        list[LearnedInterventionProfile],
        CounterfactualEvidenceScope,
    ]:
        if machine_type is not None:
            machine_type_profiles = await maintenance_outcome_service.learn(
                session,
                machine_type=machine_type,
                limit=history_limit,
            )
            if machine_type_profiles:
                return (
                    machine_type_profiles,
                    CounterfactualEvidenceScope.MACHINE_TYPE,
                )

        global_profiles = await maintenance_outcome_service.learn(
            session,
            limit=history_limit,
        )
        return (
            global_profiles,
            CounterfactualEvidenceScope.GLOBAL,
        )


counterfactual_maintenance_service = CounterfactualMaintenanceService()
