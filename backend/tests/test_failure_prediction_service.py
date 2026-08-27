import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.failure.matching import FailureMatchScore
from app.health.persistence import PersistenceResult
from app.health.scoring import (
    HealthScoreResult,
    MachineHealthState,
)
from app.services.failure_matching import FailureMatch
from app.services.failure_prediction import (
    failure_prediction_service,
)
from app.services.machine_health import (
    MachineHealthResult,
)


def make_health_result(
    *,
    machine_id: uuid.UUID,
    with_match: bool = True,
) -> MachineHealthResult:
    best_match = None

    if with_match:
        fingerprint = SimpleNamespace(
            id=uuid.uuid4(),
            machine_id=machine_id,
            failure_type=(
                "spindle_bearing_degradation"
            ),
            machine_type="cnc_milling",
            title=(
                "CNC spindle bearing degradation"
            ),
            confidence=0.92,
            failure_time=None,
        )

        best_match = FailureMatch(
            fingerprint=fingerprint,
            score=FailureMatchScore(
                overall_similarity=0.90,
                sensor_similarity=0.88,
                deviation_similarity=0.85,
                drift_similarity=0.92,
                correlation_similarity=0.80,
                trajectory_similarity=0.91,
            ),
        )

    return MachineHealthResult(
        machine_id=machine_id,
        health=HealthScoreResult(
            health_score=35.0,
            risk_score=0.65,
            state=MachineHealthState.DEGRADED,
            early_warning=True,
            components={},
        ),
        persistence=PersistenceResult(
            score=0.70,
            event_count=5,
            deviation_count=2,
            drift_count=3,
            anomalous_count=5,
            duration_seconds=900.0,
        ),
        deviation_score=0.60,
        drift_score=0.75,
        failure_match_score=(
            0.90 if with_match else 0.0
        ),
        best_failure_match=best_match,
    )


def test_prediction_identifies_likely_failure():
    machine_id = uuid.uuid4()

    health_result = make_health_result(
        machine_id=machine_id,
    )

    with patch(
        "app.services.failure_prediction."
        "machine_health_service.assess",
        new=AsyncMock(
            return_value=health_result
        ),
    ):
        result = asyncio.run(
            failure_prediction_service.predict(
                AsyncMock(),
                machine_id=machine_id,
            )
        )

    assert (
        result.likely_failure_type
        == "spindle_bearing_degradation"
    )

    assert (
        result.likely_failure_title
        == "CNC spindle bearing degradation"
    )

    assert result.failure_match_score == pytest.approx(
        0.90
    )

    assert (
        result.historical_match_confidence
        == pytest.approx(0.92)
    )

    assert result.risk.risk_score > 0.60
    assert result.risk.confidence > 0.60


def test_prediction_contains_explainable_evidence():
    machine_id = uuid.uuid4()

    health_result = make_health_result(
        machine_id=machine_id,
    )

    with patch(
        "app.services.failure_prediction."
        "machine_health_service.assess",
        new=AsyncMock(
            return_value=health_result
        ),
    ):
        result = asyncio.run(
            failure_prediction_service.predict(
                AsyncMock(),
                machine_id=machine_id,
            )
        )

    assert (
        result.evidence["deviation_score"]
        == pytest.approx(0.60)
    )

    assert (
        result.evidence["drift_score"]
        == pytest.approx(0.75)
    )

    assert (
        result.evidence["persistence_score"]
        == pytest.approx(0.70)
    )

    historical = (
        result.evidence["historical_failure"]
    )

    assert historical[
        "similarity"
    ] == pytest.approx(0.90)

    assert historical[
        "trajectory_similarity"
    ] == pytest.approx(0.91)


def test_prediction_without_historical_match():
    machine_id = uuid.uuid4()

    health_result = make_health_result(
        machine_id=machine_id,
        with_match=False,
    )

    with patch(
        "app.services.failure_prediction."
        "machine_health_service.assess",
        new=AsyncMock(
            return_value=health_result
        ),
    ):
        result = asyncio.run(
            failure_prediction_service.predict(
                AsyncMock(),
                machine_id=machine_id,
            )
        )

    assert result.likely_failure_type is None
    assert result.likely_failure_title is None
    assert (
        result.historical_match_confidence
        is None
    )
    assert result.failure_match_score == 0.0

    assert (
        "historical_failure"
        not in result.evidence
    )


def test_prediction_passes_limits_to_health_service():
    machine_id = uuid.uuid4()

    health_result = make_health_result(
        machine_id=machine_id,
    )

    assess = AsyncMock(
        return_value=health_result
    )

    with patch(
        "app.services.failure_prediction."
        "machine_health_service.assess",
        new=assess,
    ):
        asyncio.run(
            failure_prediction_service.predict(
                AsyncMock(),
                machine_id=machine_id,
                machine_type="cnc_milling",
                event_limit=50,
                library_limit=200,
            )
        )

    kwargs = assess.await_args.kwargs

    assert kwargs["machine_id"] == machine_id
    assert kwargs["machine_type"] == "cnc_milling"
    assert kwargs["event_limit"] == 50
    assert kwargs["library_limit"] == 200



