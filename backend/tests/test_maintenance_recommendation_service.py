import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.maintenance.decision import (
    MaintenanceActionType,
    MaintenanceDecision,
    MaintenancePriority,
)
from app.services.maintenance_recommendation import (
    maintenance_recommendation_service,
)


def make_explanation_result(
    machine_id: uuid.UUID,
):
    prediction = SimpleNamespace(
        likely_failure_type=(
            "spindle_bearing_degradation"
        ),
        failure_match_score=0.90,
        risk=SimpleNamespace(
            risk_score=0.80,
            confidence=0.85,
        ),
    )

    explanation = SimpleNamespace(
        primary_driver="Sensor: vibration",
        root_cause_hints=[
            SimpleNamespace(
                cause="Possible bearing degradation",
            )
        ],
        evidence=[
            SimpleNamespace(
                category=SimpleNamespace(
                    value="sensor"
                ),
                name="Sensor: vibration",
            ),
            SimpleNamespace(
                category=SimpleNamespace(
                    value="drift"
                ),
                name="Behavioral drift",
            ),
        ],
    )

    return SimpleNamespace(
        machine_id=machine_id,
        prediction=prediction,
        current_fingerprint=None,
        explanation=explanation,
    )


def test_recommendation_builds_decision():
    machine_id = uuid.uuid4()

    explanation_result = (
        make_explanation_result(machine_id)
    )

    with patch(
        "app.services.maintenance_recommendation."
        "failure_explanation_service.explain",
        new=AsyncMock(
            return_value=explanation_result
        ),
    ):
        result = asyncio.run(
            maintenance_recommendation_service.recommend(
                AsyncMock(),
                machine_id=machine_id,
            )
        )

    assert result.machine_id == machine_id

    assert (
        result.explanation_result
        is explanation_result
    )

    assert isinstance(
        result.decision,
        MaintenanceDecision,
    )

    assert (
        result.decision.priority
        == MaintenancePriority.IMMEDIATE
    )

    assert (
        result.decision.action_type
        == MaintenanceActionType.STOP_AND_INSPECT
    )


def test_recommendation_contains_failure():
    machine_id = uuid.uuid4()

    explanation_result = (
        make_explanation_result(machine_id)
    )

    with patch(
        "app.services.maintenance_recommendation."
        "failure_explanation_service.explain",
        new=AsyncMock(
            return_value=explanation_result
        ),
    ):
        result = asyncio.run(
            maintenance_recommendation_service.recommend(
                AsyncMock(),
                machine_id=machine_id,
            )
        )

    assert (
        result.decision.predicted_failure
        == "spindle_bearing_degradation"
    )

    assert (
        "spindle_bearing_degradation"
        in result.decision.recommended_action
    )


def test_recommendation_contains_explanation_signals():
    machine_id = uuid.uuid4()

    explanation_result = (
        make_explanation_result(machine_id)
    )

    with patch(
        "app.services.maintenance_recommendation."
        "failure_explanation_service.explain",
        new=AsyncMock(
            return_value=explanation_result
        ),
    ):
        result = asyncio.run(
            maintenance_recommendation_service.recommend(
                AsyncMock(),
                machine_id=machine_id,
            )
        )

    assert (
        "Sensor: vibration"
        in result.decision.affected_signals
    )

    assert (
        "Behavioral drift"
        in result.decision.affected_signals
    )

    assert result.decision.root_cause_hints == [
        "Possible bearing degradation"
    ]


def test_recommendation_passes_limits():
    machine_id = uuid.uuid4()

    explanation_result = (
        make_explanation_result(machine_id)
    )

    explain = AsyncMock(
        return_value=explanation_result
    )

    with patch(
        "app.services.maintenance_recommendation."
        "failure_explanation_service.explain",
        new=explain,
    ):
        asyncio.run(
            maintenance_recommendation_service.recommend(
                AsyncMock(),
                machine_id=machine_id,
                machine_type="cnc_milling",
                event_limit=50,
                library_limit=200,
            )
        )

    kwargs = explain.await_args.kwargs

    assert kwargs["machine_id"] == machine_id
    assert kwargs["machine_type"] == "cnc_milling"
    assert kwargs["event_limit"] == 50
    assert kwargs["library_limit"] == 200


@pytest.mark.parametrize(
    "event_limit,library_limit",
    [
        (0, 500),
        (-1, 500),
        (100, 0),
        (100, -1),
    ],
)
def test_recommendation_rejects_invalid_limits(
    event_limit,
    library_limit,
):
    with pytest.raises(ValueError):
        asyncio.run(
            maintenance_recommendation_service.recommend(
                AsyncMock(),
                machine_id=uuid.uuid4(),
                event_limit=event_limit,
                library_limit=library_limit,
            )
        )
