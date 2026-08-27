import pytest

from app.prediction.failure_risk import (
    FailureRiskInput,
    FailureRiskLevel,
    FailureTrend,
    failure_risk_scorer,
)


def test_low_failure_risk():
    result = failure_risk_scorer.score(
        FailureRiskInput(
            health_risk_score=0.10,
            failure_match_score=0.10,
            persistence_score=0.10,
            deviation_score=0.10,
            drift_score=0.10,
        )
    )

    assert result.risk_score == pytest.approx(
        0.10
    )
    assert result.level == FailureRiskLevel.LOW
    assert result.trend == FailureTrend.IMPROVING


def test_high_predictive_failure_risk():
    result = failure_risk_scorer.score(
        FailureRiskInput(
            health_risk_score=0.70,
            failure_match_score=0.90,
            persistence_score=0.75,
            deviation_score=0.60,
            drift_score=0.80,
        )
    )

    expected = (
        0.70 * 0.30
        + 0.90 * 0.35
        + 0.75 * 0.15
        + 0.60 * 0.08
        + 0.80 * 0.12
    )

    assert result.risk_score == pytest.approx(
        round(expected, 4)
    )
    assert result.level == FailureRiskLevel.CRITICAL
    assert result.trend == FailureTrend.WORSENING


def test_failure_match_is_strong_predictive_signal():
    result = failure_risk_scorer.score(
        FailureRiskInput(
            health_risk_score=0.45,
            failure_match_score=1.0,
            persistence_score=0.50,
            deviation_score=0.40,
            drift_score=0.50,
        )
    )

    assert result.components[
        "failure_match"
    ] == pytest.approx(0.35)

    assert result.confidence > 0.60


def test_no_failure_match_reduces_confidence():
    with_match = failure_risk_scorer.score(
        FailureRiskInput(
            health_risk_score=0.60,
            failure_match_score=0.90,
            persistence_score=0.60,
            deviation_score=0.50,
            drift_score=0.70,
        )
    )

    without_match = failure_risk_scorer.score(
        FailureRiskInput(
            health_risk_score=0.60,
            failure_match_score=0.0,
            persistence_score=0.60,
            deviation_score=0.50,
            drift_score=0.70,
        )
    )

    assert (
        with_match.confidence
        > without_match.confidence
    )

    assert (
        with_match.risk_score
        > without_match.risk_score
    )


def test_values_are_clamped():
    result = failure_risk_scorer.score(
        FailureRiskInput(
            health_risk_score=2.0,
            failure_match_score=3.0,
            persistence_score=-1.0,
            deviation_score=4.0,
            drift_score=2.0,
        )
    )

    assert 0.0 <= result.risk_score <= 1.0
    assert 0.0 <= result.confidence <= 1.0


def test_moderate_stable_failure_risk():
    result = failure_risk_scorer.score(
        FailureRiskInput(
            health_risk_score=0.35,
            failure_match_score=0.40,
            persistence_score=0.35,
            deviation_score=0.30,
            drift_score=0.35,
        )
    )

    assert result.level == FailureRiskLevel.MODERATE
    assert result.trend == FailureTrend.STABLE
