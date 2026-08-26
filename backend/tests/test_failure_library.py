import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.models.behavior_event import (
    BehaviorEvent,
    BehaviorEventType,
    BehaviorSeverity,
)
from app.models.failure_fingerprint import FailureFingerprint
from app.services.failure_library import (
    failure_library_service,
)


def make_event(
    *,
    event_type: BehaviorEventType,
    score: float,
    start: datetime,
    evidence: dict,
) -> BehaviorEvent:
    return BehaviorEvent(
        id=uuid.uuid4(),
        machine_id=uuid.uuid4(),
        event_type=event_type,
        severity=BehaviorSeverity.ANOMALOUS,
        score=score,
        baseline_version="3",
        window_start=start,
        window_end=start + timedelta(minutes=5),
        summary="test event",
        evidence=evidence,
        created_at=start,
    )


def test_create_failure_fingerprint_from_memory() -> None:
    async def run() -> None:
        machine_id = uuid.uuid4()

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
            score=0.45,
            start=start,
            evidence={
                "top_sensors": [
                    {
                        "sensor": "vibration",
                        "score": 0.91,
                        "mean_zscore": 9.2,
                    },
                    {
                        "sensor": "temperature",
                        "score": 0.72,
                        "mean_zscore": 5.4,
                    },
                ],
                "top_correlation_shifts": [
                    {
                        "relationship": "rpm__vibration",
                        "delta": 0.31,
                    }
                ],
            },
        )

        drift = make_event(
            event_type=BehaviorEventType.DRIFT,
            score=0.74,
            start=start + timedelta(minutes=5),
            evidence={
                "state": "drifting",
                "top_signals": [
                    {
                        "signal": "vibration__mean_zscore",
                        "score": 0.88,
                        "state": "drifting",
                    },
                    {
                        "signal": "overall_deviation",
                        "score": 0.74,
                        "state": "drifting",
                    },
                ],
            },
        )

        stored = FailureFingerprint(
            id=uuid.uuid4(),
            machine_id=machine_id,
            failure_type="bearing_degradation",
            machine_type="cnc",
            title="Bearing degradation",
            description=(
                "Historical bearing degradation pattern"
            ),
            confidence=0.95,
            baseline_version="3",
            trajectory_start=start,
            trajectory_end=start + timedelta(minutes=10),
            failure_time=start + timedelta(minutes=15),
            dominant_sensors=[],
            deviation_signature={},
            drift_signature={},
            correlation_signature={},
            trajectory_summary={},
            evidence={},
        )

        with (
            patch(
                "app.services.failure_library."
                "behavior_event_repository.list_for_machine",
                new=AsyncMock(
                    return_value=[
                        drift,
                        deviation,
                    ]
                ),
            ) as memory_mock,
            patch(
                "app.services.failure_library."
                "failure_fingerprint_repository.create",
                new=AsyncMock(
                    return_value=stored
                ),
            ) as create_mock,
        ):
            result = (
                await failure_library_service.create_from_memory(
                    AsyncMock(),
                    machine_id=machine_id,
                    failure_type="bearing_degradation",
                    machine_type="cnc",
                    title="Bearing degradation",
                    description=(
                        "Historical bearing degradation pattern"
                    ),
                    confidence=0.95,
                    failure_time=(
                        start
                        + timedelta(minutes=15)
                    ),
                )
            )

        assert result is stored

        memory_mock.assert_awaited_once()
        create_mock.assert_awaited_once()

        kwargs = create_mock.await_args.kwargs

        assert kwargs["machine_id"] == machine_id
        assert (
            kwargs["failure_type"]
            == "bearing_degradation"
        )
        assert kwargs["machine_type"] == "cnc"
        assert kwargs["baseline_version"] == "3"

        assert (
            kwargs["dominant_sensors"][0]["sensor"]
            == "vibration"
        )

        assert (
            kwargs["deviation_signature"]["event_count"]
            == 1
        )

        assert (
            kwargs["drift_signature"]["event_count"]
            == 1
        )

        assert (
            kwargs["drift_signature"]["states"]
            == ["drifting"]
        )

        relationships = kwargs[
            "correlation_signature"
        ]["relationships"]

        assert (
            relationships[0]["relationship"]
            == "rpm__vibration"
        )

        assert (
            kwargs["trajectory_summary"]["event_count"]
            == 2
        )

        assert (
            kwargs["evidence"]["event_count"]
            == 2
        )

    asyncio.run(run())


def test_create_failure_fingerprint_without_memory_fails() -> None:
    async def run() -> None:
        with patch(
            "app.services.failure_library."
            "behavior_event_repository.list_for_machine",
            new=AsyncMock(
                return_value=[]
            ),
        ):
            with pytest.raises(
                ValueError,
                match=(
                    "No behavioral memory events available"
                ),
            ):
                await failure_library_service.create_from_memory(
                    AsyncMock(),
                    machine_id=uuid.uuid4(),
                    failure_type="bearing_degradation",
                    title="Bearing degradation",
                )

    asyncio.run(run())


def test_non_behavioral_events_are_rejected() -> None:
    async def run() -> None:
        start = datetime(
            2026,
            8,
            26,
            10,
            0,
            tzinfo=timezone.utc,
        )

        maintenance = make_event(
            event_type=BehaviorEventType.MAINTENANCE,
            score=0.0,
            start=start,
            evidence={},
        )

        with patch(
            "app.services.failure_library."
            "behavior_event_repository.list_for_machine",
            new=AsyncMock(
                return_value=[maintenance]
            ),
        ):
            with pytest.raises(
                ValueError,
                match=(
                    "No behavioral memory events available"
                ),
            ):
                await failure_library_service.create_from_memory(
                    AsyncMock(),
                    machine_id=uuid.uuid4(),
                    failure_type="bearing_degradation",
                    title="Bearing degradation",
                )

    asyncio.run(run())
