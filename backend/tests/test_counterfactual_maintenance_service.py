import asyncio
import uuid
from types import SimpleNamespace

from app.maintenance.outcome import (
    LearnedInterventionProfile,
    LearnedOutcomeState,
)
from app.services.counterfactual_maintenance import (
    CounterfactualMaintenanceService,
)


def test_service_uses_machine_type_history(monkeypatch):
    async def run():
        service = CounterfactualMaintenanceService()
        machine_id = uuid.uuid4()

        async def fake_assess(*args, **kwargs):
            return SimpleNamespace(
                health=SimpleNamespace(
                    health_score=58.0,
                    risk_score=0.70,
                ),
                deviation_score=0.45,
                drift_score=0.61,
                failure_match_score=0.50,
            )

        profile = LearnedInterventionProfile(
            intervention_type="bearing_replacement",
            sample_count=12,
            average_recovery_score=0.60,
            average_risk_reduction=0.52,
            average_drift_reduction=0.44,
            average_health_improvement=0.30,
            success_rate=0.90,
            confidence=1.0,
            state=LearnedOutcomeState.HIGHLY_EFFECTIVE,
        )

        calls = []

        async def fake_learn(*args, **kwargs):
            calls.append(kwargs)
            return [profile]

        monkeypatch.setattr(
            "app.services.counterfactual_maintenance.machine_health_service.assess",
            fake_assess,
        )
        monkeypatch.setattr(
            "app.services.counterfactual_maintenance.maintenance_outcome_service.learn",
            fake_learn,
        )

        result = await service.analyze(
            object(),
            machine_id=machine_id,
            machine_type="cnc",
        )

        assert result.machine_id == machine_id
        assert result.analysis.recommended_intervention == "bearing_replacement"
        assert result.analysis.candidates[0].evidence_scope.value == "machine_type"
        assert calls[0]["machine_type"] == "cnc"

    asyncio.run(run())


def test_service_falls_back_to_global_history(monkeypatch):
    async def run():
        service = CounterfactualMaintenanceService()
        machine_id = uuid.uuid4()

        async def fake_assess(*args, **kwargs):
            return SimpleNamespace(
                health=SimpleNamespace(
                    health_score=64.0,
                    risk_score=0.57,
                ),
                deviation_score=0.40,
                drift_score=0.48,
                failure_match_score=0.36,
            )

        profile = LearnedInterventionProfile(
            intervention_type="inspection",
            sample_count=4,
            average_recovery_score=0.20,
            average_risk_reduction=0.12,
            average_drift_reduction=0.10,
            average_health_improvement=0.08,
            success_rate=0.50,
            confidence=0.40,
            state=LearnedOutcomeState.LIMITED_EFFECT,
        )

        calls = []

        async def fake_learn(*args, **kwargs):
            calls.append(kwargs)
            if kwargs.get("machine_type") == "cnc":
                return []
            return [profile]

        monkeypatch.setattr(
            "app.services.counterfactual_maintenance.machine_health_service.assess",
            fake_assess,
        )
        monkeypatch.setattr(
            "app.services.counterfactual_maintenance.maintenance_outcome_service.learn",
            fake_learn,
        )

        result = await service.analyze(
            object(),
            machine_id=machine_id,
            machine_type="cnc",
        )

        assert len(calls) == 2
        assert result.analysis.candidates[0].evidence_scope.value == "global"

    asyncio.run(run())


def test_service_filters_candidate_interventions(monkeypatch):
    async def run():
        service = CounterfactualMaintenanceService()

        async def fake_assess(*args, **kwargs):
            return SimpleNamespace(
                health=SimpleNamespace(
                    health_score=50.0,
                    risk_score=0.75,
                ),
                deviation_score=0.55,
                drift_score=0.65,
                failure_match_score=0.60,
            )

        def make_profile(name):
            return LearnedInterventionProfile(
                intervention_type=name,
                sample_count=10,
                average_recovery_score=0.50,
                average_risk_reduction=0.40,
                average_drift_reduction=0.35,
                average_health_improvement=0.25,
                success_rate=0.80,
                confidence=0.80,
                state=LearnedOutcomeState.EFFECTIVE,
            )

        async def fake_learn(*args, **kwargs):
            return [
                make_profile("bearing_replacement"),
                make_profile("lubrication"),
            ]

        monkeypatch.setattr(
            "app.services.counterfactual_maintenance.machine_health_service.assess",
            fake_assess,
        )
        monkeypatch.setattr(
            "app.services.counterfactual_maintenance.maintenance_outcome_service.learn",
            fake_learn,
        )

        result = await service.analyze(
            object(),
            machine_id=uuid.uuid4(),
            candidate_interventions=["lubrication"],
        )

        assert [
            item.intervention_type
            for item in result.analysis.candidates
        ] == ["lubrication"]

    asyncio.run(run())
