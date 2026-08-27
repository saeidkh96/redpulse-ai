import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.health.persistence import (
    behavioral_persistence_scorer,
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
    start: datetime,
    end: datetime,
) -> BehaviorEvent:
    return BehaviorEvent(
        id=uuid.uuid4(),
        machine_id=uuid.uuid4(),
        event_type=event_type,
        severity=severity,
        score=0.5,
        baseline_version="3",
        window_start=start,
        window_end=end,
        summary="test event",
        evidence={},
        created_at=start,
    )


def test_no_behavioral_history_has_zero_persistence():
    result = behavioral_persistence_scorer.score([])

    assert result.score == pytest.approx(0.0)
    assert result.event_count == 0
    assert result.deviation_count == 0
    assert result.drift_count == 0
    assert result.anomalous_count == 0
    assert result.duration_seconds is None


def test_single_deviation_has_low_persistence():
    start = datetime(
        2026,
        8,
        27,
        10,
        0,
        tzinfo=timezone.utc,
    )

    event = make_event(
        event_type=BehaviorEventType.DEVIATION,
        severity=BehaviorSeverity.ANOMALOUS,
        start=start,
        end=start + timedelta(minutes=5),
    )

    result = behavioral_persistence_scorer.score(
        [event]
    )

    assert result.event_count == 1
    assert result.deviation_count == 1
    assert result.drift_count == 0
    assert result.anomalous_count == 1

    assert result.score == pytest.approx(
        0.515
    )


def test_repeated_deviations_increase_persistence():
    start = datetime(
        2026,
        8,
        27,
        10,
        0,
        tzinfo=timezone.utc,
    )

    events = [
        make_event(
            event_type=BehaviorEventType.DEVIATION,
            severity=BehaviorSeverity.ANOMALOUS,
            start=start + timedelta(minutes=index * 5),
            end=start + timedelta(minutes=(index + 1) * 5),
        )
        for index in range(5)
    ]

    result = behavioral_persistence_scorer.score(
        events
    )

    assert result.event_count == 5
    assert result.deviation_count == 5
    assert result.drift_count == 0

    assert result.score == pytest.approx(
        0.675
    )


def test_deviation_and_drift_have_stronger_persistence():
    start = datetime(
        2026,
        8,
        27,
        10,
        0,
        tzinfo=timezone.utc,
    )

    events = [
        make_event(
            event_type=BehaviorEventType.DEVIATION,
            severity=BehaviorSeverity.ANOMALOUS,
            start=start,
            end=start + timedelta(minutes=5),
        ),
        make_event(
            event_type=BehaviorEventType.DRIFT,
            severity=BehaviorSeverity.ANOMALOUS,
            start=start + timedelta(minutes=5),
            end=start + timedelta(minutes=15),
        ),
    ]

    result = behavioral_persistence_scorer.score(
        events
    )

    assert result.event_count == 2
    assert result.deviation_count == 1
    assert result.drift_count == 1
    assert result.anomalous_count == 2

    assert result.score == pytest.approx(
        0.68
    )

    assert result.duration_seconds == pytest.approx(
        900.0
    )


def test_persistence_score_is_bounded():
    start = datetime(
        2026,
        8,
        27,
        10,
        0,
        tzinfo=timezone.utc,
    )

    events = [
        make_event(
            event_type=BehaviorEventType.DRIFT,
            severity=BehaviorSeverity.ANOMALOUS,
            start=start + timedelta(minutes=index),
            end=start + timedelta(minutes=index + 1),
        )
        for index in range(30)
    ]

    result = behavioral_persistence_scorer.score(
        events
    )

    assert 0.0 <= result.score <= 1.0
    assert result.event_count == 30
