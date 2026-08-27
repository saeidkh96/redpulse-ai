from app.maintenance.counterfactual import (
    CounterfactualEvidenceScope,
    CounterfactualMaintenanceEngine,
)
from app.maintenance.outcome import (
    LearnedInterventionProfile,
    LearnedOutcomeState,
)
from app.maintenance.verification import MaintenanceSnapshot


def _profile(
    *,
    intervention_type: str,
    recovery: float,
    risk: float,
    drift: float,
    health: float,
    success_rate: float,
    confidence: float,
    samples: int,
) -> LearnedInterventionProfile:
    return LearnedInterventionProfile(
        intervention_type=intervention_type,
        sample_count=samples,
        average_recovery_score=recovery,
        average_risk_reduction=risk,
        average_drift_reduction=drift,
        average_health_improvement=health,
        success_rate=success_rate,
        confidence=confidence,
        state=LearnedOutcomeState.EFFECTIVE,
    )


def test_counterfactual_engine_builds_no_maintenance_trajectory():
    engine = CounterfactualMaintenanceEngine()
    current = MaintenanceSnapshot(
        health_score=65.0,
        risk_score=0.62,
        deviation_score=0.48,
        drift_score=0.55,
        failure_match_score=0.44,
    )

    result = engine.analyze(
        current=current,
        profiles=[],
        horizon_steps=5,
        evidence_scope=CounterfactualEvidenceScope.GLOBAL,
    )

    assert result.no_maintenance.predicted_health_score < current.health_score
    assert result.no_maintenance.predicted_risk_score > current.risk_score
    assert result.no_maintenance.predicted_drift_score > current.drift_score
    assert result.recommended_intervention is None
    assert result.recommendation_confidence == 0.0


def test_counterfactual_engine_ranks_stronger_intervention_first():
    engine = CounterfactualMaintenanceEngine()
    current = MaintenanceSnapshot(
        health_score=55.0,
        risk_score=0.72,
        deviation_score=0.50,
        drift_score=0.66,
        failure_match_score=0.58,
    )

    profiles = [
        _profile(
            intervention_type="lubrication",
            recovery=0.12,
            risk=0.08,
            drift=0.06,
            health=0.05,
            success_rate=0.40,
            confidence=0.50,
            samples=5,
        ),
        _profile(
            intervention_type="bearing_replacement",
            recovery=0.62,
            risk=0.55,
            drift=0.48,
            health=0.32,
            success_rate=0.90,
            confidence=0.90,
            samples=18,
        ),
    ]

    result = engine.analyze(
        current=current,
        profiles=profiles,
        horizon_steps=5,
        evidence_scope=CounterfactualEvidenceScope.MACHINE_TYPE,
    )

    assert result.recommended_intervention == "bearing_replacement"
    assert result.candidates[0].estimated_intervention_benefit > result.candidates[1].estimated_intervention_benefit
    assert result.candidates[0].historical_support == 18
    assert result.candidates[0].avoided_risk > 0.0
    assert result.candidates[0].avoided_drift > 0.0


def test_global_history_reduces_candidate_confidence():
    engine = CounterfactualMaintenanceEngine()
    current = MaintenanceSnapshot(
        health_score=60.0,
        risk_score=0.60,
        deviation_score=0.40,
        drift_score=0.50,
        failure_match_score=0.35,
    )
    profile = _profile(
        intervention_type="bearing_replacement",
        recovery=0.50,
        risk=0.40,
        drift=0.35,
        health=0.25,
        success_rate=0.80,
        confidence=0.80,
        samples=10,
    )

    typed = engine.analyze(
        current=current,
        profiles=[profile],
        horizon_steps=5,
        evidence_scope=CounterfactualEvidenceScope.MACHINE_TYPE,
    )
    global_result = engine.analyze(
        current=current,
        profiles=[profile],
        horizon_steps=5,
        evidence_scope=CounterfactualEvidenceScope.GLOBAL,
    )

    assert typed.candidates[0].confidence > global_result.candidates[0].confidence


def test_longer_horizon_is_more_conservative():
    engine = CounterfactualMaintenanceEngine()
    current = MaintenanceSnapshot(
        health_score=70.0,
        risk_score=0.50,
        deviation_score=0.35,
        drift_score=0.42,
        failure_match_score=0.30,
    )

    short = engine.analyze(
        current=current,
        profiles=[],
        horizon_steps=2,
        evidence_scope=CounterfactualEvidenceScope.GLOBAL,
    )
    long = engine.analyze(
        current=current,
        profiles=[],
        horizon_steps=20,
        evidence_scope=CounterfactualEvidenceScope.GLOBAL,
    )

    assert long.no_maintenance.predicted_health_score < short.no_maintenance.predicted_health_score
    assert long.no_maintenance.predicted_risk_score >= short.no_maintenance.predicted_risk_score
    assert long.no_maintenance.confidence <= short.no_maintenance.confidence
