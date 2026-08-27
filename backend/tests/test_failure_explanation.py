import pytest

from app.explainability.failure_explanation import (
    EvidenceCategory,
    failure_explanation_engine,
)


def make_explanation():
    return failure_explanation_engine.explain(
        prediction_evidence={
            "machine_health_state": "critical",
            "deviation_score": 0.60,
            "drift_score": 0.75,
            "persistence_score": 0.70,
            "historical_failure": {
                "similarity": 0.90,
            },
        },
        risk_components={
            "health": 0.20,
            "failure_match": 0.35,
            "persistence": 0.105,
            "deviation": 0.048,
            "drift": 0.09,
        },
        dominant_sensors=[
            {
                "sensor": "spindle_vibration",
                "occurrences": 3,
                "mean_score": 0.88,
                "max_score": 0.95,
            },
            {
                "sensor": "spindle_temperature",
                "occurrences": 2,
                "mean_score": 0.65,
                "max_score": 0.75,
            },
        ],
        drift_signature={
            "dominant_signals": [
                {
                    "signal": (
                        "spindle_vibration__mean_zscore"
                    ),
                    "occurrences": 2,
                    "mean_score": 0.82,
                    "max_score": 0.90,
                }
            ]
        },
        correlation_signature={
            "relationships": [
                {
                    "relationship": (
                        "spindle_vibration"
                        "__spindle_temperature"
                    ),
                    "occurrences": 2,
                    "mean_delta": 0.55,
                    "max_delta": 0.70,
                }
            ]
        },
        trajectory_summary={
            "event_count": 6,
            "duration_seconds": 1800.0,
        },
    )


def test_explanation_contains_ranked_evidence():
    result = make_explanation()

    assert result.evidence

    contributions = [
        item.contribution
        for item in result.evidence
    ]

    assert contributions == sorted(
        contributions,
        reverse=True,
    )


def test_dominant_sensor_becomes_evidence():
    result = make_explanation()

    sensor_items = [
        item
        for item in result.evidence
        if item.category
        == EvidenceCategory.SENSOR
    ]

    assert sensor_items

    assert (
        sensor_items[0].name
        == "Sensor: spindle_vibration"
    )

    assert (
        sensor_items[0].value
        == pytest.approx(0.88)
    )


def test_historical_match_is_explained():
    result = make_explanation()

    historical = [
        item
        for item in result.evidence
        if item.category
        == EvidenceCategory.HISTORICAL_MATCH
    ]

    assert len(historical) == 1
    assert historical[0].value == pytest.approx(
        0.90
    )


def test_root_cause_hints_are_generated():
    result = make_explanation()

    causes = {
        item.cause
        for item in result.root_cause_hints
    }

    assert "spindle_vibration" in causes

    assert (
        "spindle_vibration__mean_zscore"
        in causes
    )


def test_summary_contains_primary_driver():
    result = make_explanation()

    assert result.primary_driver is not None

    assert (
        result.primary_driver
        in result.summary
    )


def test_empty_evidence_is_safe():
    result = failure_explanation_engine.explain(
        prediction_evidence={},
        risk_components={},
    )

    assert result.primary_driver is None
    assert result.evidence == []
    assert result.root_cause_hints == []

    assert (
        "No significant"
        in result.summary
    )
