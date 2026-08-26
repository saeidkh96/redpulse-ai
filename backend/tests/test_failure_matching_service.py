import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.models.behavior_event import (
    BehaviorEventType,
    BehaviorSeverity,
)
from app.services.failure_matching import (
    failure_matching_service,
)


def make_event(
    *,
    event_type,
    score,
    start,
    evidence,
):
    return SimpleNamespace(
        id=uuid.uuid4(),
        machine_id=uuid.uuid4(),
        event_type=event_type,
        severity=BehaviorSeverity.ANOMALOUS,
        score=score,
        baseline_version="3",
        window_start=start,
        window_end=start + timedelta(minutes=5),
        evidence=evidence,
        created_at=start,
    )


def make_candidate(
    *,
    failure_type,
    vibration,
    drift_score,
):
    return SimpleNamespace(
        id=uuid.uuid4(),
        machine_id=uuid.uuid4(),
        failure_type=failure_type,
        machine_type="cnc_milling",
        title=failure_type,
        dominant_sensors=[
            {
                "sensor": "vibration",
                "mean_score": vibration,
            }
        ],
        deviation_signature={
            "max_score": 0.40,
            "mean_score": 0.40,
            "severities": ["anomalous"],
        },
        drift_signature={
            "max_score": drift_score,
            "mean_score": drift_score,
            "states": ["drifting"],
            "dominant_signals": [
                {
                    "signal": "vibration__mean_zscore",
                    "mean_score": vibration,
                }
            ],
        },
        correlation_signature={
            "relationships": [
                {
                    "relationship": "rpm__vibration",
                    "mean_delta": 0.30,
                }
            ],
        },
        trajectory_summary={
            "max_deviation_score": 0.40,
            "mean_deviation_score": 0.40,
            "max_drift_score": drift_score,
            "mean_drift_score": drift_score,
            "duration_seconds": 600.0,
        },
    )


def test_match_machine_ranks_best_failure_first():
    async def run():
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
            score=0.40,
            start=start,
            evidence={
                "top_sensors": [
                    {
                        "sensor": "vibration",
                        "score": 0.85,
                        "mean_zscore": 8.0,
                    }
                ],
                "top_correlation_shifts": [
                    {
                        "relationship": "rpm__vibration",
                        "delta": 0.30,
                    }
                ],
            },
        )

        drift = make_event(
            event_type=BehaviorEventType.DRIFT,
            score=0.70,
            start=start + timedelta(minutes=5),
            evidence={
                "state": "drifting",
                "top_signals": [
                    {
                        "signal": "vibration__mean_zscore",
                        "score": 0.85,
                        "state": "drifting",
                    }
                ],
            },
        )

        strong_match = make_candidate(
            failure_type="spindle_bearing_degradation",
            vibration=0.85,
            drift_score=0.70,
        )

        weak_match = make_candidate(
            failure_type="electrical_instability",
            vibration=0.15,
            drift_score=0.10,
        )

        with (
            patch(
                "app.services.failure_matching."
                "behavior_event_repository."
                "list_for_machine",
                new=AsyncMock(
                    return_value=[
                        drift,
                        deviation,
                    ]
                ),
            ),
            patch(
                "app.services.failure_matching."
                "failure_fingerprint_repository."
                "list_library",
                new=AsyncMock(
                    return_value=[
                        weak_match,
                        strong_match,
                    ]
                ),
            ),
        ):
            result = (
                await failure_matching_service.match_machine(
                    object(),
                    machine_id=machine_id,
                    top_k=2,
                )
            )

        assert result.machine_id == machine_id
        assert result.candidate_count == 2
        assert len(result.matches) == 2

        assert (
            result.matches[0]
            .fingerprint.failure_type
            == "spindle_bearing_degradation"
        )

        assert (
            result.matches[0]
            .score.overall_similarity
            >
            result.matches[1]
            .score.overall_similarity
        )

    asyncio.run(run())


def test_match_machine_applies_top_k():
    async def run():
        machine_id = uuid.uuid4()

        start = datetime(
            2026,
            8,
            26,
            10,
            0,
            tzinfo=timezone.utc,
        )

        event = make_event(
            event_type=BehaviorEventType.DEVIATION,
            score=0.40,
            start=start,
            evidence={
                "top_sensors": [
                    {
                        "sensor": "vibration",
                        "score": 0.80,
                        "mean_zscore": 7.0,
                    }
                ],
                "top_correlation_shifts": [],
            },
        )

        candidates = [
            make_candidate(
                failure_type=f"failure_{index}",
                vibration=0.80 - index * 0.05,
                drift_score=0.60,
            )
            for index in range(4)
        ]

        with (
            patch(
                "app.services.failure_matching."
                "behavior_event_repository."
                "list_for_machine",
                new=AsyncMock(
                    return_value=[event]
                ),
            ),
            patch(
                "app.services.failure_matching."
                "failure_fingerprint_repository."
                "list_library",
                new=AsyncMock(
                    return_value=candidates
                ),
            ),
        ):
            result = (
                await failure_matching_service.match_machine(
                    object(),
                    machine_id=machine_id,
                    top_k=2,
                )
            )

        assert result.candidate_count == 4
        assert len(result.matches) == 2

    asyncio.run(run())


def test_match_machine_without_memory_fails():
    async def run():
        with patch(
            "app.services.failure_matching."
            "behavior_event_repository."
            "list_for_machine",
            new=AsyncMock(
                return_value=[]
            ),
        ):
            with pytest.raises(
                ValueError,
                match="No behavioral memory",
            ):
                await failure_matching_service.match_machine(
                    object(),
                    machine_id=uuid.uuid4(),
                )

    asyncio.run(run())


def test_match_machine_filters_minimum_similarity():
    async def run():
        machine_id = uuid.uuid4()

        start = datetime(
            2026,
            8,
            26,
            10,
            0,
            tzinfo=timezone.utc,
        )

        event = make_event(
            event_type=BehaviorEventType.DEVIATION,
            score=0.40,
            start=start,
            evidence={
                "top_sensors": [
                    {
                        "sensor": "vibration",
                        "score": 0.85,
                        "mean_zscore": 8.0,
                    }
                ],
                "top_correlation_shifts": [],
            },
        )

        unrelated = SimpleNamespace(
            id=uuid.uuid4(),
            machine_id=uuid.uuid4(),
            failure_type="unrelated_failure",
            machine_type="cnc_milling",
            title="Unrelated failure",
            dominant_sensors=[
                {
                    "sensor": "load",
                    "mean_score": 0.05,
                }
            ],
            deviation_signature={
                "max_score": 0.05,
                "mean_score": 0.05,
                "severities": ["normal"],
            },
            drift_signature={
                "max_score": 0.05,
                "mean_score": 0.05,
                "states": ["stable"],
                "dominant_signals": [],
            },
            correlation_signature={
                "relationships": []
            },
            trajectory_summary={
                "max_deviation_score": 0.05,
                "mean_deviation_score": 0.05,
                "max_drift_score": 0.05,
                "mean_drift_score": 0.05,
                "duration_seconds": 60.0,
            },
        )

        with (
            patch(
                "app.services.failure_matching."
                "behavior_event_repository."
                "list_for_machine",
                new=AsyncMock(
                    return_value=[event]
                ),
            ),
            patch(
                "app.services.failure_matching."
                "failure_fingerprint_repository."
                "list_library",
                new=AsyncMock(
                    return_value=[unrelated]
                ),
            ),
        ):
            result = (
                await failure_matching_service.match_machine(
                    object(),
                    machine_id=machine_id,
                    minimum_similarity=0.90,
                )
            )

        assert result.candidate_count == 1
        assert result.matches == []

    asyncio.run(run())
