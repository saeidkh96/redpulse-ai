import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.health.scoring import MachineHealthState
from app.models.behavior_event import (
    BehaviorEvent,
    BehaviorEventType,
    BehaviorSeverity,
)
from types import SimpleNamespace

from app.failure.fingerprint import FailureFingerprintData
from app.services.failure_matching import (
    FailureMatch,
    FailureMatchScore,
    FailureMatchingResult,
)
from app.services.machine_health import (
    machine_health_service,
)


def make_event(
    *,
    machine_id: uuid.UUID,
    event_type: BehaviorEventType,
    score: float,
    start: datetime,
    end: datetime,
) -> BehaviorEvent:
    return BehaviorEvent(
        id=uuid.uuid4(),
        machine_id=machine_id,
        event_type=event_type,
        severity=BehaviorSeverity.ANOMALOUS,
        score=score,
        baseline_version="3",
        window_start=start,
        window_end=end,
        summary="test behavioral event",
        evidence={},
        created_at=start,
    )


def make_match(
    *,
    machine_id: uuid.UUID,
    similarity: float,
) -> FailureMatch:
    fingerprint = SimpleNamespace(
        id=uuid.uuid4(),
        machine_id=machine_id,
        failure_type="spindle_bearing_degradation",
        machine_type="cnc_milling",
        title="Historical spindle bearing degradation",
        confidence=0.92,
        failure_time=None,
    )

    return FailureMatch(
        fingerprint=fingerprint,
        score=FailureMatchScore(
            overall_similarity=similarity,
            sensor_similarity=similarity,
            deviation_similarity=similarity,
            drift_similarity=similarity,
            correlation_similarity=similarity,
            trajectory_similarity=similarity,
        ),
    )


def make_current_fingerprint() -> FailureFingerprintData:
    return FailureFingerprintData(
        baseline_version="3",
        trajectory_start=None,
        trajectory_end=None,
        dominant_sensors=[],
        deviation_signature={},
        drift_signature={},
        correlation_signature={},
        trajectory_summary={},
        evidence={},
    )

def test_health_service_combines_behavior_and_failure_match():
    machine_id = uuid.uuid4()

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
            machine_id=machine_id,
            event_type=BehaviorEventType.DEVIATION,
            score=0.60,
            start=start,
            end=start + timedelta(minutes=5),
        ),
        make_event(
            machine_id=machine_id,
            event_type=BehaviorEventType.DRIFT,
            score=0.70,
            start=start + timedelta(minutes=5),
            end=start + timedelta(minutes=15),
        ),
    ]

    match = make_match(
        machine_id=machine_id,
        similarity=0.80,
    )

    matching_result = FailureMatchingResult(
        machine_id=machine_id,
        current_fingerprint=make_current_fingerprint(),
        matches=[match],
        candidate_count=1,
    )

    with (
        patch(
            "app.services.machine_health."
            "behavior_event_repository.list_for_machine",
            new=AsyncMock(return_value=events),
        ),
        patch(
            "app.services.machine_health."
            "failure_matching_service.match_machine",
            new=AsyncMock(
                return_value=matching_result
            ),
        ),
    ):
        result = __import__(
            "asyncio"
        ).run(
            machine_health_service.assess(
                AsyncMock(),
                machine_id=machine_id,
                machine_type="cnc_milling",
            )
        )

    assert result.machine_id == machine_id

    assert result.deviation_score == pytest.approx(
        0.60
    )
    assert result.drift_score == pytest.approx(
        0.70
    )

    assert result.persistence.score == pytest.approx(
        0.68
    )

    assert result.failure_match_score == pytest.approx(
        0.80
    )

    assert result.best_failure_match is match

    expected_risk = (
        0.60 * 0.25
        + 0.70 * 0.30
        + 0.80 * 0.35
        + 0.68 * 0.10
    )

    assert result.health.risk_score == pytest.approx(
        round(expected_risk, 4)
    )

    assert result.health.health_score == pytest.approx(
        round(
            (1.0 - expected_risk) * 100.0,
            2,
        )
    )

    assert result.health.state == (
        MachineHealthState.CRITICAL
    )

    assert result.health.early_warning is True


def test_health_service_without_behavior_is_healthy():
    machine_id = uuid.uuid4()

    matching_mock = AsyncMock()

    with (
        patch(
            "app.services.machine_health."
            "behavior_event_repository.list_for_machine",
            new=AsyncMock(return_value=[]),
        ),
        patch(
            "app.services.machine_health."
            "failure_matching_service.match_machine",
            new=matching_mock,
        ),
    ):
        result = __import__(
            "asyncio"
        ).run(
            machine_health_service.assess(
                AsyncMock(),
                machine_id=machine_id,
            )
        )

    assert result.deviation_score == pytest.approx(
        0.0
    )
    assert result.drift_score == pytest.approx(
        0.0
    )
    assert result.failure_match_score == pytest.approx(
        0.0
    )
    assert result.persistence.score == pytest.approx(
        0.0
    )

    assert result.best_failure_match is None

    assert result.health.health_score == pytest.approx(
        100.0
    )
    assert result.health.risk_score == pytest.approx(
        0.0
    )
    assert result.health.state == (
        MachineHealthState.HEALTHY
    )
    assert result.health.early_warning is False

    matching_mock.assert_not_awaited()


def test_health_service_uses_latest_behavior_scores():
    machine_id = uuid.uuid4()

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
            machine_id=machine_id,
            event_type=BehaviorEventType.DEVIATION,
            score=0.20,
            start=start,
            end=start + timedelta(minutes=5),
        ),
        make_event(
            machine_id=machine_id,
            event_type=BehaviorEventType.DEVIATION,
            score=0.75,
            start=start + timedelta(minutes=10),
            end=start + timedelta(minutes=15),
        ),
        make_event(
            machine_id=machine_id,
            event_type=BehaviorEventType.DRIFT,
            score=0.30,
            start=start + timedelta(minutes=5),
            end=start + timedelta(minutes=10),
        ),
        make_event(
            machine_id=machine_id,
            event_type=BehaviorEventType.DRIFT,
            score=0.85,
            start=start + timedelta(minutes=15),
            end=start + timedelta(minutes=20),
        ),
    ]

    matching_result = FailureMatchingResult(
        machine_id=machine_id,
        current_fingerprint=make_current_fingerprint(),
        matches=[],
        candidate_count=0,
    )

    with (
        patch(
            "app.services.machine_health."
            "behavior_event_repository.list_for_machine",
            new=AsyncMock(return_value=events),
        ),
        patch(
            "app.services.machine_health."
            "failure_matching_service.match_machine",
            new=AsyncMock(
                return_value=matching_result
            ),
        ),
    ):
        result = __import__(
            "asyncio"
        ).run(
            machine_health_service.assess(
                AsyncMock(),
                machine_id=machine_id,
            )
        )

    assert result.deviation_score == pytest.approx(
        0.75
    )

    assert result.drift_score == pytest.approx(
        0.85
    )

    assert result.failure_match_score == pytest.approx(
        0.0
    )


def test_health_service_rejects_invalid_limits():
    machine_id = uuid.uuid4()

    with pytest.raises(
        ValueError,
        match="event_limit must be at least 1",
    ):
        __import__(
            "asyncio"
        ).run(
            machine_health_service.assess(
                AsyncMock(),
                machine_id=machine_id,
                event_limit=0,
            )
        )

    with pytest.raises(
        ValueError,
        match="library_limit must be at least 1",
    ):
        __import__(
            "asyncio"
        ).run(
            machine_health_service.assess(
                AsyncMock(),
                machine_id=machine_id,
                library_limit=0,
            )
        )




