import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.failure.fingerprint import (
    failure_fingerprint_builder,
)
from app.models.behavior_event import (
    BehaviorEvent,
    BehaviorEventType,
    BehaviorSeverity,
)


def make_event(
    *,
    event_type: BehaviorEventType,
    severity: BehaviorSeverity,
    score: float,
    start: datetime,
    end: datetime,
    evidence: dict,
) -> BehaviorEvent:
    return BehaviorEvent(
        id=uuid.uuid4(),
        machine_id=uuid.uuid4(),
        event_type=event_type,
        severity=severity,
        score=score,
        baseline_version="3",
        window_start=start,
        window_end=end,
        summary="test",
        evidence=evidence,
        created_at=start,
    )


def test_build_failure_fingerprint() -> None:
    start = datetime(
        2026,
        8,
        26,
        10,
        0,
        tzinfo=timezone.utc,
    )

    deviation = make_event(
        event_type=BehaviorEventType.DEVIATION,
        severity=BehaviorSeverity.ANOMALOUS,
        score=0.42,
        start=start,
        end=start + timedelta(minutes=5),
        evidence={
            "top_sensors": [
                {
                    "sensor": "vibration",
                    "score": 0.90,
                    "mean_zscore": 8.0,
                },
                {
                    "sensor": "temperature",
                    "score": 0.70,
                    "mean_zscore": 5.0,
                },
            ],
            "top_correlation_shifts": [
                {
                    "relationship": "rpm__vibration",
                    "delta": 0.35,
                }
            ],
        },
    )

    drift = make_event(
        event_type=BehaviorEventType.DRIFT,
        severity=BehaviorSeverity.ANOMALOUS,
        score=0.72,
        start=start + timedelta(minutes=5),
        end=start + timedelta(minutes=15),
        evidence={
            "state": "drifting",
            "top_signals": [
                {
                    "signal": "vibration__mean_zscore",
                    "score": 0.86,
                    "state": "drifting",
                },
                {
                    "signal": "overall_deviation",
                    "score": 0.72,
                    "state": "drifting",
                },
            ],
        },
    )

    result = failure_fingerprint_builder.build(
        [
            deviation,
            drift,
        ]
    )

    assert result.baseline_version == "3"

    assert (
        result.trajectory_start
        == start
    )

    assert (
        result.trajectory_end
        == start
        + timedelta(minutes=15)
    )

    assert (
        result.dominant_sensors[0]["sensor"]
        == "vibration"
    )

    assert (
        result.deviation_signature["event_count"]
        == 1
    )

    assert (
        result.deviation_signature["max_score"]
        == pytest.approx(0.42)
    )

    assert (
        result.drift_signature["event_count"]
        == 1
    )

    assert (
        result.drift_signature["states"]
        == ["drifting"]
    )

    relationships = (
        result.correlation_signature[
            "relationships"
        ]
    )

    assert (
        relationships[0]["relationship"]
        == "rpm__vibration"
    )

    assert (
        result.trajectory_summary[
            "event_count"
        ]
        == 2
    )

    assert (
        result.trajectory_summary[
            "deviation_event_count"
        ]
        == 1
    )

    assert (
        result.trajectory_summary[
            "drift_event_count"
        ]
        == 1
    )

    assert (
        result.trajectory_summary[
            "max_deviation_score"
        ]
        == pytest.approx(0.42)
    )

    assert (
        result.trajectory_summary[
            "mean_deviation_score"
        ]
        == pytest.approx(0.42)
    )

    assert (
        result.trajectory_summary[
            "max_drift_score"
        ]
        == pytest.approx(0.72)
    )

    assert (
        result.trajectory_summary[
            "mean_drift_score"
        ]
        == pytest.approx(0.72)
    )

    assert (
        result.evidence["event_count"]
        == 2
    )


def test_empty_events_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="events must not be empty",
    ):
        failure_fingerprint_builder.build([])

