import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.failure.fingerprint import FailureFingerprintData
from app.prediction.failure_risk import (
    FailureRiskLevel,
    FailureRiskResult,
    FailureTrend,
)
from app.services.failure_prediction import (
    FailurePredictionResult,
)
from app.services.failure_explanation import (
    failure_explanation_service,
)


def make_prediction(
    *,
    machine_id: uuid.UUID,
) -> FailurePredictionResult:
    return FailurePredictionResult(
        machine_id=machine_id,
        likely_failure_type="spindle_bearing_degradation",
        likely_failure_title="Spindle bearing degradation",
        risk=FailureRiskResult(
            risk_score=0.78,
            confidence=0.82,
            level=FailureRiskLevel.CRITICAL,
            trend=FailureTrend.WORSENING,
            components={
                "health": 0.20,
                "failure_match": 0.35,
                "persistence": 0.10,
                "deviation": 0.05,
                "drift": 0.08,
            },
        ),
        historical_match_confidence=0.92,
        failure_match_score=0.90,
        evidence={
            "machine_health_score": 30.0,
            "machine_health_state": "critical",
            "machine_risk_score": 0.70,
            "deviation_score": 0.60,
            "drift_score": 0.75,
            "persistence_score": 0.70,
            "persistence_event_count": 5,
            "historical_failure": {
                "fingerprint_id": str(uuid.uuid4()),
                "failure_type": (
                    "spindle_bearing_degradation"
                ),
                "similarity": 0.90,
                "sensor_similarity": 0.88,
                "deviation_similarity": 0.85,
                "drift_similarity": 0.92,
                "correlation_similarity": 0.80,
                "trajectory_similarity": 0.91,
            },
        },
    )


def make_event(
    *,
    machine_id: uuid.UUID,
    event_type,
    score: float,
    start: datetime,
    end: datetime,
):
    return SimpleNamespace(
        id=uuid.uuid4(),
        machine_id=machine_id,
        event_type=event_type,
        score=score,
        severity=SimpleNamespace(
            value="anomalous"
        ),
        baseline_version="3",
        window_start=start,
        window_end=end,
        created_at=start,
        summary="test event",
        evidence={},
    )


def make_fingerprint() -> FailureFingerprintData:
    return FailureFingerprintData(
        baseline_version="3",
        trajectory_start=None,
        trajectory_end=None,
        dominant_sensors=[
            {
                "sensor": "vibration",
                "occurrences": 3,
                "mean_score": 0.88,
                "max_score": 0.95,
                "mean_zscore": 8.0,
                "max_zscore": 10.0,
            },
            {
                "sensor": "temperature",
                "occurrences": 2,
                "mean_score": 0.65,
                "max_score": 0.75,
                "mean_zscore": 5.0,
                "max_zscore": 6.0,
            },
        ],
        deviation_signature={
            "vibration": 0.80,
        },
        drift_signature={
            "vibration": 0.75,
            "temperature": 0.55,
        },
        correlation_signature={
            "vibration_temperature": 0.70,
        },
        trajectory_summary={
            "event_count": 5,
            "deviation_count": 2,
            "drift_count": 3,
        },
        evidence={},
    )


def test_explanation_service_builds_explanation():
    from app.models.behavior_event import (
        BehaviorEventType,
    )

    machine_id = uuid.uuid4()

    prediction = make_prediction(
        machine_id=machine_id,
    )

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
            score=0.75,
            start=start + timedelta(minutes=5),
            end=start + timedelta(minutes=15),
        ),
    ]

    fingerprint = make_fingerprint()

    with (
        patch(
            "app.services.failure_explanation."
            "failure_prediction_service.predict",
            new=AsyncMock(
                return_value=prediction
            ),
        ),
        patch(
            "app.services.failure_explanation."
            "behavior_event_repository.list_for_machine",
            new=AsyncMock(
                return_value=events
            ),
        ),
        patch(
            "app.services.failure_explanation."
            "failure_fingerprint_builder.build",
            return_value=fingerprint,
        ),
    ):
        result = asyncio.run(
            failure_explanation_service.explain(
                AsyncMock(),
                machine_id=machine_id,
            )
        )

    assert result.machine_id == machine_id
    assert result.prediction == prediction
    assert result.current_fingerprint == fingerprint
    assert result.explanation is not None


def test_explanation_service_passes_behavioral_evidence():
    from app.models.behavior_event import (
        BehaviorEventType,
    )

    machine_id = uuid.uuid4()

    prediction = make_prediction(
        machine_id=machine_id,
    )

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
            event_type=BehaviorEventType.DRIFT,
            score=0.80,
            start=start,
            end=start + timedelta(minutes=10),
        ),
    ]

    fingerprint = make_fingerprint()

    with (
        patch(
            "app.services.failure_explanation."
            "failure_prediction_service.predict",
            new=AsyncMock(
                return_value=prediction
            ),
        ),
        patch(
            "app.services.failure_explanation."
            "behavior_event_repository.list_for_machine",
            new=AsyncMock(
                return_value=events
            ),
        ),
        patch(
            "app.services.failure_explanation."
            "failure_fingerprint_builder.build",
            return_value=fingerprint,
        ),
        patch(
            "app.services.failure_explanation."
            "failure_explanation_engine.explain",
            return_value=SimpleNamespace(),
        ) as explain,
    ):
        asyncio.run(
            failure_explanation_service.explain(
                AsyncMock(),
                machine_id=machine_id,
            )
        )

    kwargs = explain.call_args.kwargs

    assert kwargs["dominant_sensors"] == [
        {
            "sensor": "vibration",
            "occurrences": 3,
            "mean_score": 0.88,
            "max_score": 0.95,
            "mean_zscore": 8.0,
            "max_zscore": 10.0,
        },
        {
            "sensor": "temperature",
            "occurrences": 2,
            "mean_score": 0.65,
            "max_score": 0.75,
            "mean_zscore": 5.0,
            "max_zscore": 6.0,
        },
    ]

    assert kwargs["drift_signature"] == {
        "vibration": 0.75,
        "temperature": 0.55,
    }

    assert kwargs["correlation_signature"] == {
        "vibration_temperature": 0.70,
    }

    assert kwargs["trajectory_summary"] == {
        "event_count": 5,
        "deviation_count": 2,
        "drift_count": 3,
    }


def test_explanation_service_handles_no_behavior_events():
    machine_id = uuid.uuid4()

    prediction = make_prediction(
        machine_id=machine_id,
    )

    with (
        patch(
            "app.services.failure_explanation."
            "failure_prediction_service.predict",
            new=AsyncMock(
                return_value=prediction
            ),
        ),
        patch(
            "app.services.failure_explanation."
            "behavior_event_repository.list_for_machine",
            new=AsyncMock(
                return_value=[]
            ),
        ),
        patch(
            "app.services.failure_explanation."
            "failure_explanation_engine.explain",
            return_value=SimpleNamespace(),
        ) as explain,
    ):
        result = asyncio.run(
            failure_explanation_service.explain(
                AsyncMock(),
                machine_id=machine_id,
            )
        )

    assert result.current_fingerprint is None

    kwargs = explain.call_args.kwargs

    assert kwargs["dominant_sensors"] == []
    assert kwargs["drift_signature"] == {}
    assert kwargs["correlation_signature"] == {}
    assert kwargs["trajectory_summary"] == {}


def test_explanation_service_passes_limits():
    machine_id = uuid.uuid4()

    prediction = make_prediction(
        machine_id=machine_id,
    )

    predict = AsyncMock(
        return_value=prediction
    )

    events = AsyncMock(
        return_value=[]
    )

    with (
        patch(
            "app.services.failure_explanation."
            "failure_prediction_service.predict",
            new=predict,
        ),
        patch(
            "app.services.failure_explanation."
            "behavior_event_repository.list_for_machine",
            new=events,
        ),
    ):
        asyncio.run(
            failure_explanation_service.explain(
                AsyncMock(),
                machine_id=machine_id,
                machine_type="cnc_milling",
                event_limit=50,
                library_limit=200,
            )
        )

    kwargs = predict.await_args.kwargs

    assert kwargs["machine_id"] == machine_id
    assert kwargs["machine_type"] == "cnc_milling"
    assert kwargs["event_limit"] == 50
    assert kwargs["library_limit"] == 200

    assert (
        events.await_args.kwargs["limit"]
        == 50
    )


@pytest.mark.parametrize(
    "event_limit,library_limit",
    [
        (0, 500),
        (-1, 500),
        (100, 0),
        (100, -1),
    ],
)
def test_explanation_service_rejects_invalid_limits(
    event_limit,
    library_limit,
):
    with pytest.raises(ValueError):
        asyncio.run(
            failure_explanation_service.explain(
                AsyncMock(),
                machine_id=uuid.uuid4(),
                event_limit=event_limit,
                library_limit=library_limit,
            )
        )


