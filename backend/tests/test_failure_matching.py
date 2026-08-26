import pytest

from app.failure.matching import (
    failure_trajectory_matcher,
)


def make_fingerprint(
    *,
    vibration=0.85,
    temperature=0.70,
    deviation=0.40,
    drift=0.70,
    drift_state="drifting",
    correlation=0.30,
    max_deviation_score=0.40,
    mean_deviation_score=0.35,
    max_drift_score=0.75,
    mean_drift_score=0.65,
    duration=600.0,
):
    return {
        "dominant_sensors": [
            {
                "sensor": "vibration",
                "mean_score": vibration,
            },
            {
                "sensor": "temperature",
                "mean_score": temperature,
            },
        ],
        "deviation_signature": {
            "max_score": deviation,
            "mean_score": deviation,
            "severities": ["anomalous"],
        },
        "drift_signature": {
            "max_score": drift,
            "mean_score": drift,
            "states": [drift_state],
            "dominant_signals": [
                {
                    "signal": "vibration__mean_zscore",
                    "mean_score": vibration,
                },
                {
                    "signal": "temperature__mean_zscore",
                    "mean_score": temperature,
                },
            ],
        },
        "correlation_signature": {
            "relationships": [
                {
                    "relationship": "rpm__vibration",
                    "mean_delta": correlation,
                }
            ],
        },
        "trajectory_summary": {
            "max_deviation_score": max_deviation_score,
            "mean_deviation_score": mean_deviation_score,
            "max_drift_score": max_drift_score,
            "mean_drift_score": mean_drift_score,
            "duration_seconds": duration,
        },
    }


def test_identical_failure_trajectory_has_full_similarity():
    current = make_fingerprint()
    historical = make_fingerprint()

    result = failure_trajectory_matcher.match(
        current,
        historical,
    )

    assert result.overall_similarity == pytest.approx(
        1.0
    )
    assert result.sensor_similarity == pytest.approx(
        1.0
    )
    assert result.deviation_similarity == pytest.approx(
        1.0
    )
    assert result.drift_similarity == pytest.approx(
        1.0
    )
    assert result.correlation_similarity == pytest.approx(
        1.0
    )
    assert result.trajectory_similarity == pytest.approx(
        1.0
    )


def test_similar_failure_trajectory_scores_high():
    current = make_fingerprint()

    historical = make_fingerprint(
        vibration=0.80,
        temperature=0.66,
        deviation=0.44,
        drift=0.65,
        correlation=0.27,
        max_deviation_score=0.44,
        mean_deviation_score=0.39,
        max_drift_score=0.71,
        mean_drift_score=0.60,
        duration=650.0,
    )

    result = failure_trajectory_matcher.match(
        current,
        historical,
    )

    assert result.overall_similarity > 0.80
    assert result.sensor_similarity > 0.90
    assert result.drift_similarity > 0.85
    assert result.trajectory_similarity > 0.80


def test_unrelated_failure_trajectory_scores_lower():
    current = make_fingerprint()

    historical = {
        "dominant_sensors": [
            {
                "sensor": "load",
                "mean_score": 0.15,
            },
            {
                "sensor": "current",
                "mean_score": 0.20,
            },
        ],
        "deviation_signature": {
            "max_score": 0.05,
            "mean_score": 0.04,
            "severities": ["normal"],
        },
        "drift_signature": {
            "max_score": 0.08,
            "mean_score": 0.05,
            "states": ["stable"],
            "dominant_signals": [
                {
                    "signal": "load__mean_zscore",
                    "mean_score": 0.10,
                }
            ],
        },
        "correlation_signature": {
            "relationships": [
                {
                    "relationship": "load__current",
                    "mean_delta": 0.02,
                }
            ],
        },
        "trajectory_summary": {
            "max_deviation_score": 0.05,
            "mean_deviation_score": 0.04,
            "max_drift_score": 0.10,
            "mean_drift_score": 0.06,
            "duration_seconds": 120.0,
        },
    }

    result = failure_trajectory_matcher.match(
        current,
        historical,
    )

    assert result.overall_similarity < 0.50
    assert result.sensor_similarity == pytest.approx(
        0.0
    )
    assert result.correlation_similarity == pytest.approx(
        0.0
    )


def test_empty_fingerprints_do_not_crash():
    current = {}
    historical = {}

    result = failure_trajectory_matcher.match(
        current,
        historical,
    )

    assert result.overall_similarity == pytest.approx(
        0.0
    )
    assert result.sensor_similarity == pytest.approx(
        0.0
    )
    assert result.deviation_similarity == pytest.approx(
        0.0
    )
    assert result.drift_similarity == pytest.approx(
        0.0
    )
    assert result.correlation_similarity == pytest.approx(
        0.0
    )
    assert result.trajectory_similarity == pytest.approx(
        0.0
    )


def test_different_sensor_structure_reduces_similarity():
    current = make_fingerprint()

    historical = make_fingerprint()
    historical["dominant_sensors"] = [
        {
            "sensor": "vibration",
            "mean_score": 0.85,
        },
        {
            "sensor": "current",
            "mean_score": 0.70,
        },
    ]

    result = failure_trajectory_matcher.match(
        current,
        historical,
    )

    assert 0.0 < result.sensor_similarity < 1.0
    assert result.overall_similarity < 1.0

