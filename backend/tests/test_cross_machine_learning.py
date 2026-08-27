from app.fleet.cross_machine import (
    CrossMachineEvidenceScope,
    CrossMachineLearningEngine,
    PeerMachineEvidence,
)
from app.maintenance.outcome import LearnedInterventionProfile, LearnedOutcomeState


def profile(name: str, recovery: float, confidence: float, samples: int):
    return LearnedInterventionProfile(
        intervention_type=name,
        sample_count=samples,
        average_recovery_score=recovery,
        average_risk_reduction=max(0.0, recovery * 0.8),
        average_drift_reduction=max(0.0, recovery * 0.7),
        average_health_improvement=max(0.0, recovery * 0.5),
        success_rate=0.8,
        confidence=confidence,
        state=LearnedOutcomeState.EFFECTIVE,
    )


def test_cross_machine_engine_ranks_stronger_peer_evidence_first():
    engine = CrossMachineLearningEngine()
    evidence = [
        PeerMachineEvidence(
            machine_id="peer-1",
            machine_type="cnc",
            manufacturer="acme",
            model="x1",
            similarity_score=1.0,
            intervention_type="bearing_replacement",
            outcome_score=0.9,
            outcome_label="highly_effective",
        ),
        PeerMachineEvidence(
            machine_id="peer-2",
            machine_type="cnc",
            manufacturer="acme",
            model="x1",
            similarity_score=0.9,
            intervention_type="bearing_replacement",
            outcome_score=0.8,
            outcome_label="effective",
        ),
        PeerMachineEvidence(
            machine_id="peer-3",
            machine_type="cnc",
            manufacturer="other",
            model="x2",
            similarity_score=0.6,
            intervention_type="lubrication",
            outcome_score=0.2,
            outcome_label="limited_effect",
        ),
    ]

    result = engine.analyze(
        target_machine_id="target",
        machine_type="cnc",
        peer_evidence=evidence,
        historical_profiles=[
            profile("bearing_replacement", 0.75, 0.9, 12),
            profile("lubrication", 0.25, 0.6, 8),
        ],
        evidence_scope=CrossMachineEvidenceScope.PEER_GROUP,
    )

    assert result.recommended_intervention == "bearing_replacement"
    assert result.peer_count == 3
    assert result.interventions[0].evidence_score > result.interventions[1].evidence_score


def test_cross_machine_engine_can_use_history_without_peer_records():
    engine = CrossMachineLearningEngine()

    result = engine.analyze(
        target_machine_id="target",
        machine_type="cnc",
        peer_evidence=[],
        historical_profiles=[profile("inspection", 0.4, 0.7, 10)],
        evidence_scope=CrossMachineEvidenceScope.MACHINE_TYPE,
    )

    assert result.recommended_intervention == "inspection"
    assert result.peer_count == 0
    assert result.interventions[0].peer_support == 0


def test_global_scope_reduces_evidence_strength():
    engine = CrossMachineLearningEngine()
    evidence = [
        PeerMachineEvidence(
            machine_id="peer",
            machine_type="cnc",
            manufacturer=None,
            model=None,
            similarity_score=0.8,
            intervention_type="replacement",
            outcome_score=0.8,
            outcome_label="effective",
        )
    ]
    profiles = [profile("replacement", 0.7, 0.8, 10)]

    peer = engine.analyze(
        target_machine_id="target",
        machine_type="cnc",
        peer_evidence=evidence,
        historical_profiles=profiles,
        evidence_scope=CrossMachineEvidenceScope.PEER_GROUP,
    )
    global_result = engine.analyze(
        target_machine_id="target",
        machine_type="cnc",
        peer_evidence=evidence,
        historical_profiles=profiles,
        evidence_scope=CrossMachineEvidenceScope.GLOBAL,
    )

    assert peer.interventions[0].evidence_score > global_result.interventions[0].evidence_score
