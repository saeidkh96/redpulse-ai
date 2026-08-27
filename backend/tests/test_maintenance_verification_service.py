import asyncio
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.health.persistence import PersistenceResult
from app.health.scoring import (
    HealthScoreResult,
    MachineHealthState,
)
from app.maintenance.verification import (
    MaintenanceSnapshot,
    RecoveryState,
)
from app.services.machine_health import (
    MachineHealthResult,
)
from app.services.maintenance_verification import (
    maintenance_verification_service,
)


def make_before_snapshot() -> MaintenanceSnapshot:
    return MaintenanceSnapshot(
        health_score=30.0,
        risk_score=0.80,
        deviation_score=0.75,
        drift_score=0.70,
        failure_match_score=0.90,
    )


def make_health_result(
    *,
    health_score: float = 80.0,
    risk_score: float = 0.20,
    deviation_score: float = 0.15,
    drift_score: float = 0.10,
    failure_match_score: float = 0.20,
) -> MachineHealthResult:
    health = HealthScoreResult(
        health_score=health_score,
        risk_score=risk_score,
        state=MachineHealthState.HEALTHY,
        early_warning=(
            risk_score >= 0.40
        ),
        components={},
    )

    persistence = PersistenceResult(
        score=0.10,
        event_count=1,
        deviation_count=1,
        drift_count=0,
        anomalous_count=0,
        duration_seconds=60.0,
    )

    return MachineHealthResult(
        machine_id=uuid.uuid4(),
        health=health,
        persistence=persistence,
        deviation_score=deviation_score,
        drift_score=drift_score,
        failure_match_score=failure_match_score,
        best_failure_match=None,
    )


def test_verification_service_detects_recovery():
    machine_id = uuid.uuid4()
    before = make_before_snapshot()

    health_result = make_health_result()

    with patch(
        "app.services.maintenance_verification."
        "machine_health_service.assess",
        new=AsyncMock(
            return_value=health_result
        ),
    ):
        result = asyncio.run(
            maintenance_verification_service.verify(
                AsyncMock(),
                machine_id=machine_id,
                before=before,
            )
        )

    assert result.machine_id == machine_id
    assert result.before == before

    assert result.after.health_score == pytest.approx(
        80.0
    )

    assert result.after.risk_score == pytest.approx(
        0.20
    )

    assert (
        result.after.deviation_score
        == pytest.approx(0.15)
    )

    assert result.after.drift_score == pytest.approx(
        0.10
    )

    assert (
        result.after.failure_match_score
        == pytest.approx(0.20)
    )

    assert (
        result.verification.state
        == RecoveryState.RECOVERED
    )

    assert (
        result.verification.recovery_score
        > 0.35
    )

    assert (
        result.verification.health_improvement
        > 0.0
    )

    assert (
        result.verification.risk_reduction
        > 0.0
    )


def test_verification_service_detects_worsening():
    machine_id = uuid.uuid4()

    before = MaintenanceSnapshot(
        health_score=80.0,
        risk_score=0.20,
        deviation_score=0.15,
        drift_score=0.10,
        failure_match_score=0.20,
    )

    health_result = make_health_result(
        health_score=40.0,
        risk_score=0.75,
        deviation_score=0.70,
        drift_score=0.65,
        failure_match_score=0.85,
    )

    with patch(
        "app.services.maintenance_verification."
        "machine_health_service.assess",
        new=AsyncMock(
            return_value=health_result
        ),
    ):
        result = asyncio.run(
            maintenance_verification_service.verify(
                AsyncMock(),
                machine_id=machine_id,
                before=before,
            )
        )

    assert (
        result.verification.state
        == RecoveryState.WORSENED
    )

    assert (
        result.verification.recovery_score
        < -0.10
    )

    assert (
        result.verification.health_improvement
        < 0.0
    )

    assert (
        result.verification.risk_reduction
        < 0.0
    )


def test_verification_service_passes_limits():
    machine_id = uuid.uuid4()
    before = make_before_snapshot()

    health_result = make_health_result()

    assess = AsyncMock(
        return_value=health_result
    )

    with patch(
        "app.services.maintenance_verification."
        "machine_health_service.assess",
        new=assess,
    ):
        asyncio.run(
            maintenance_verification_service.verify(
                AsyncMock(),
                machine_id=machine_id,
                before=before,
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


def test_verification_service_rejects_invalid_event_limit():
    with pytest.raises(
        ValueError,
        match="event_limit must be at least 1",
    ):
        asyncio.run(
            maintenance_verification_service.verify(
                AsyncMock(),
                machine_id=uuid.uuid4(),
                before=make_before_snapshot(),
                event_limit=0,
            )
        )


def test_verification_service_rejects_invalid_library_limit():
    with pytest.raises(
        ValueError,
        match="library_limit must be at least 1",
    ):
        asyncio.run(
            maintenance_verification_service.verify(
                AsyncMock(),
                machine_id=uuid.uuid4(),
                before=make_before_snapshot(),
                library_limit=0,
            )
        )
