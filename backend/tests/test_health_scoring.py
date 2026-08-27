import pytest

from app.health.scoring import (
    HealthScoreInput,
    MachineHealthState,
    machine_health_scorer,
)


def test_healthy_machine_has_full_health():
    result = machine_health_scorer.score(
        HealthScoreInput(
            deviation_score=0.0,
            drift_score=0.0,
            failure_match_score=0.0,
            persistence_score=0.0,
        )
    )

    assert result.risk_score == pytest.approx(0.0)
    assert result.health_score == pytest.approx(100.0)
    assert result.state == MachineHealthState.HEALTHY
    assert result.early_warning is False


def test_maximum_risk_machine_is_critical():
    result = machine_health_scorer.score(
        HealthScoreInput(
            deviation_score=1.0,
            drift_score=1.0,
            failure_match_score=1.0,
            persistence_score=1.0,
        )
    )

    assert result.risk_score == pytest.approx(1.0)
    assert result.health_score == pytest.approx(0.0)
    assert result.state == MachineHealthState.CRITICAL
    assert result.early_warning is True


def test_failure_match_has_strong_risk_contribution():
    result = machine_health_scorer.score(
        HealthScoreInput(
            deviation_score=0.0,
            drift_score=0.0,
            failure_match_score=1.0,
            persistence_score=0.0,
        )
    )

    assert result.risk_score == pytest.approx(0.35)
    assert result.health_score == pytest.approx(65.0)
    assert result.state == MachineHealthState.WATCH
    assert result.early_warning is False


def test_combined_behavior_triggers_early_warning():
    result = machine_health_scorer.score(
        HealthScoreInput(
            deviation_score=0.60,
            drift_score=0.70,
            failure_match_score=0.80,
            persistence_score=0.50,
        )
    )

    expected_risk = (
        0.60 * 0.25
        + 0.70 * 0.30
        + 0.80 * 0.35
        + 0.50 * 0.10
    )

    assert result.risk_score == pytest.approx(
        expected_risk
    )

    assert result.health_score == pytest.approx(
        round(
            (1.0 - expected_risk) * 100.0,
            2,
        )
    )

    assert result.state == MachineHealthState.CRITICAL
    assert result.early_warning is True


def test_scores_are_clamped_to_valid_range():
    result = machine_health_scorer.score(
        HealthScoreInput(
            deviation_score=-1.0,
            drift_score=2.0,
            failure_match_score=5.0,
            persistence_score=-0.5,
        )
    )

    expected_risk = (
        0.0 * 0.25
        + 1.0 * 0.30
        + 1.0 * 0.35
        + 0.0 * 0.10
    )

    assert result.risk_score == pytest.approx(
        expected_risk
    )

    assert 0.0 <= result.health_score <= 100.0
    assert 0.0 <= result.risk_score <= 1.0


def test_component_breakdown_is_exposed():
    result = machine_health_scorer.score(
        HealthScoreInput(
            deviation_score=0.40,
            drift_score=0.50,
            failure_match_score=0.60,
            persistence_score=0.70,
        )
    )

    assert result.components["deviation"] == pytest.approx(
        0.10
    )

    assert result.components["drift"] == pytest.approx(
        0.15
    )

    assert result.components["failure_match"] == pytest.approx(
        0.21
    )

    assert result.components["persistence"] == pytest.approx(
        0.07
    )
