import pytest

from app.maintenance.outcome import (
    InterventionOutcome,
    LearnedOutcomeState,
    MaintenanceOutcomeLearningEngine,
)


def test_learning_engine_identifies_effective_action():
    engine = MaintenanceOutcomeLearningEngine()
    profile = engine.learn(
        intervention_type="bearing_replacement",
        outcomes=[
            InterventionOutcome(0.72, 0.70, 0.81, 0.48),
            InterventionOutcome(0.61, 0.63, 0.74, 0.41),
            InterventionOutcome(0.58, 0.59, 0.66, 0.39),
        ],
    )

    assert profile.intervention_type == "bearing_replacement"
    assert profile.sample_count == 3
    assert profile.success_rate == 1.0
    assert profile.state is LearnedOutcomeState.HIGHLY_EFFECTIVE
    assert profile.average_recovery_score > 0.6


def test_learning_engine_identifies_ineffective_action():
    engine = MaintenanceOutcomeLearningEngine()
    profile = engine.learn(
        intervention_type="lubrication",
        outcomes=[
            InterventionOutcome(0.01, 0.04, 0.03, 0.01),
            InterventionOutcome(-0.02, 0.01, -0.01, 0.00),
        ],
    )

    assert profile.success_rate == 0.0
    assert profile.state is LearnedOutcomeState.INEFFECTIVE


def test_learning_requires_history():
    engine = MaintenanceOutcomeLearningEngine()
    with pytest.raises(ValueError):
        engine.learn(intervention_type="inspection", outcomes=[])
