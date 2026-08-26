from app.memory.engine import behavioral_memory_engine
from app.models.behavior_event import (
    BehaviorEventType,
    BehaviorSeverity,
)


def test_normal_deviation_not_stored() -> None:
    decision = behavioral_memory_engine.from_deviation(
        overall_score=0.05,
        severity="normal",
        sensor_deviations={},
        correlation_shifts={},
    )

    assert decision.should_store is False
    assert decision.event_type is None


def test_warning_deviation_is_stored() -> None:
    decision = behavioral_memory_engine.from_deviation(
        overall_score=0.35,
        severity="warning",
        sensor_deviations={
            "vibration": {
                "mean_zscore": 4.2,
                "score": 0.8,
            },
            "temperature": {
                "mean_zscore": 2.4,
                "score": 0.5,
            },
        },
        correlation_shifts={
            "rpm__vibration": {
                "delta": 0.4,
            },
        },
    )

    assert decision.should_store is True
    assert (
        decision.event_type
        == BehaviorEventType.DEVIATION
    )
    assert (
        decision.severity
        == BehaviorSeverity.WARNING
    )

    assert (
        decision.evidence["top_sensors"][0][
            "sensor"
        ]
        == "vibration"
    )


def test_anomalous_deviation_is_stored() -> None:
    decision = behavioral_memory_engine.from_deviation(
        overall_score=0.42,
        severity="anomalous",
        sensor_deviations={
            "vibration": {
                "mean_zscore": 12.0,
                "score": 1.0,
            },
        },
        correlation_shifts={},
    )

    assert decision.should_store is True
    assert (
        decision.severity
        == BehaviorSeverity.ANOMALOUS
    )


def test_stable_drift_not_stored() -> None:
    decision = behavioral_memory_engine.from_drift(
        overall_score=0.10,
        state="stable",
        signals={},
    )

    assert decision.should_store is False


def test_emerging_drift_is_stored() -> None:
    decision = behavioral_memory_engine.from_drift(
        overall_score=0.45,
        state="emerging",
        signals={
            "vibration__mean_zscore": {
                "score": 0.7,
                "state": "drifting",
            },
            "temperature__mean_zscore": {
                "score": 0.5,
                "state": "emerging",
            },
        },
    )

    assert decision.should_store is True
    assert (
        decision.event_type
        == BehaviorEventType.DRIFT
    )
    assert (
        decision.severity
        == BehaviorSeverity.WARNING
    )


def test_drifting_state_is_anomalous_memory() -> None:
    decision = behavioral_memory_engine.from_drift(
        overall_score=0.72,
        state="drifting",
        signals={
            "vibration__mean_zscore": {
                "score": 0.86,
                "state": "drifting",
            },
        },
    )

    assert decision.should_store is True
    assert (
        decision.severity
        == BehaviorSeverity.ANOMALOUS
    )
