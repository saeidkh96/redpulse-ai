import pytest

from app.maintenance.verification import (
    MaintenanceSnapshot,
    RecoveryState,
    maintenance_verification_engine,
)


def test_recovered_state():
    before = MaintenanceSnapshot(
        health_score=30.0,
        risk_score=0.75,
        deviation_score=0.70,
        drift_score=0.75,
        failure_match_score=0.90,
    )

    after = MaintenanceSnapshot(
        health_score=85.0,
        risk_score=0.20,
        deviation_score=0.20,
        drift_score=0.15,
        failure_match_score=0.20,
    )

    result = maintenance_verification_engine.verify(
        before=before,
        after=after,
    )

    assert result.state == RecoveryState.RECOVERED
    assert result.recovery_score >= 0.35


def test_partial_recovery_state():
    before = MaintenanceSnapshot(
        health_score=45.0,
        risk_score=0.60,
        deviation_score=0.55,
        drift_score=0.60,
        failure_match_score=0.70,
    )

    after = MaintenanceSnapshot(
        health_score=60.0,
        risk_score=0.45,
        deviation_score=0.45,
        drift_score=0.45,
        failure_match_score=0.55,
    )

    result = maintenance_verification_engine.verify(
        before=before,
        after=after,
    )

    assert (
        result.state
        == RecoveryState.PARTIALLY_RECOVERED
    )

    assert 0.10 <= result.recovery_score < 0.35


def test_no_improvement_state():
    before = MaintenanceSnapshot(
        health_score=55.0,
        risk_score=0.50,
        deviation_score=0.45,
        drift_score=0.50,
        failure_match_score=0.60,
    )

    after = MaintenanceSnapshot(
        health_score=56.0,
        risk_score=0.49,
        deviation_score=0.44,
        drift_score=0.49,
        failure_match_score=0.59,
    )

    result = maintenance_verification_engine.verify(
        before=before,
        after=after,
    )

    assert (
        result.state
        == RecoveryState.NO_IMPROVEMENT
    )


def test_worsened_state():
    before = MaintenanceSnapshot(
        health_score=60.0,
        risk_score=0.40,
        deviation_score=0.35,
        drift_score=0.40,
        failure_match_score=0.50,
    )

    after = MaintenanceSnapshot(
        health_score=35.0,
        risk_score=0.75,
        deviation_score=0.70,
        drift_score=0.75,
        failure_match_score=0.85,
    )

    result = maintenance_verification_engine.verify(
        before=before,
        after=after,
    )

    assert result.state == RecoveryState.WORSENED
    assert result.recovery_score < -0.10


def test_health_improvement_is_positive_when_health_rises():
    before = MaintenanceSnapshot(
        health_score=40.0,
        risk_score=0.60,
        deviation_score=0.50,
        drift_score=0.50,
        failure_match_score=0.60,
    )

    after = MaintenanceSnapshot(
        health_score=70.0,
        risk_score=0.40,
        deviation_score=0.35,
        drift_score=0.35,
        failure_match_score=0.40,
    )

    result = maintenance_verification_engine.verify(
        before=before,
        after=after,
    )

    assert result.health_improvement == pytest.approx(
        0.30
    )


def test_risk_reduction_is_positive_when_risk_drops():
    before = MaintenanceSnapshot(
        health_score=40.0,
        risk_score=0.80,
        deviation_score=0.50,
        drift_score=0.50,
        failure_match_score=0.60,
    )

    after = MaintenanceSnapshot(
        health_score=60.0,
        risk_score=0.30,
        deviation_score=0.40,
        drift_score=0.40,
        failure_match_score=0.50,
    )

    result = maintenance_verification_engine.verify(
        before=before,
        after=after,
    )

    assert result.risk_reduction == pytest.approx(
        0.50
    )


def test_component_sum_matches_recovery_score():
    before = MaintenanceSnapshot(
        health_score=30.0,
        risk_score=0.80,
        deviation_score=0.70,
        drift_score=0.70,
        failure_match_score=0.90,
    )

    after = MaintenanceSnapshot(
        health_score=70.0,
        risk_score=0.40,
        deviation_score=0.40,
        drift_score=0.40,
        failure_match_score=0.50,
    )

    result = maintenance_verification_engine.verify(
        before=before,
        after=after,
    )

    expected = sum(
        result.components.values()
    )

    assert result.recovery_score == pytest.approx(
        round(expected, 4)
    )


def test_extreme_values_are_clamped():
    before = MaintenanceSnapshot(
        health_score=-100.0,
        risk_score=5.0,
        deviation_score=5.0,
        drift_score=5.0,
        failure_match_score=5.0,
    )

    after = MaintenanceSnapshot(
        health_score=500.0,
        risk_score=-2.0,
        deviation_score=-2.0,
        drift_score=-2.0,
        failure_match_score=-2.0,
    )

    result = maintenance_verification_engine.verify(
        before=before,
        after=after,
    )

    assert -1.0 <= result.recovery_score <= 1.0
