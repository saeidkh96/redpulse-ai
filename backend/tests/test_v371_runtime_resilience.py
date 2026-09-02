from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select, update

from app.core.database import AsyncSessionLocal, engine
from app.models.runtime_replay_execution import RuntimeReplayExecution
from app.platform_expansion_v37.durable_replay import (
    DatabaseReplayLedger,
    DurableResilientStageRunner,
)
from app.platform_expansion_v37.resilience import (
    ExecutionState,
    ExecutionToken,
    StageExecutionResult,
)


async def _cleanup(token: ExecutionToken) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(RuntimeReplayExecution).where(
                RuntimeReplayExecution.execution_key == token.key
            )
        )
        await session.commit()


async def _get_record(
    token: ExecutionToken,
) -> RuntimeReplayExecution | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RuntimeReplayExecution).where(
                RuntimeReplayExecution.execution_key == token.key
            )
        )
        return result.scalar_one_or_none()


async def _test_durable_replay_survives_runner_restart() -> None:
    unique_id = uuid.uuid4().hex

    token = ExecutionToken(
        tenant_id=f"tenant-{unique_id}",
        workflow_id="predictive-maintenance",
        stage_name="maintenance-decision",
        payload={"machine_id": unique_id},
    )

    calls = 0

    async def operation() -> dict:
        nonlocal calls
        calls += 1

        return {
            "decision": "inspect",
            "machine_id": unique_id,
        }

    try:
        runner_1 = DurableResilientStageRunner(
            DatabaseReplayLedger(AsyncSessionLocal)
        )

        first = await runner_1.run(token, operation)

        assert first.state == ExecutionState.SUCCEEDED
        assert first.replayed is False
        assert first.attempts == 1
        assert calls == 1

        runner_2 = DurableResilientStageRunner(
            DatabaseReplayLedger(AsyncSessionLocal)
        )

        second = await runner_2.run(token, operation)

        assert second.state == ExecutionState.SUCCEEDED
        assert second.replayed is True
        assert second.attempts == 1
        assert second.value == {
            "decision": "inspect",
            "machine_id": unique_id,
        }

        assert calls == 1

    finally:
        await _cleanup(token)


async def _test_durable_runner_retries_then_persists_success() -> None:
    unique_id = uuid.uuid4().hex

    token = ExecutionToken(
        tenant_id=f"tenant-{unique_id}",
        workflow_id="failure-analysis",
        stage_name="trajectory-match",
        payload={"machine_id": unique_id},
    )

    calls = 0

    async def flaky_operation() -> dict:
        nonlocal calls
        calls += 1

        if calls == 1:
            raise RuntimeError("simulated transient failure")

        return {"matched": True}

    try:
        runner_1 = DurableResilientStageRunner(
            DatabaseReplayLedger(AsyncSessionLocal)
        )

        result = await runner_1.run(
            token,
            flaky_operation,
            max_attempts=3,
        )

        assert result.state == ExecutionState.SUCCEEDED
        assert result.replayed is False
        assert result.attempts == 2
        assert calls == 2

        runner_2 = DurableResilientStageRunner(
            DatabaseReplayLedger(AsyncSessionLocal)
        )

        replayed = await runner_2.run(token, flaky_operation)

        assert replayed.state == ExecutionState.SUCCEEDED
        assert replayed.replayed is True
        assert replayed.attempts == 2
        assert calls == 2

    finally:
        await _cleanup(token)


async def _test_failed_state_persists_and_can_be_recovered() -> None:
    unique_id = uuid.uuid4().hex

    token = ExecutionToken(
        tenant_id=f"tenant-{unique_id}",
        workflow_id="maintenance-recovery",
        stage_name="decision-stage",
        payload={"machine_id": unique_id},
    )

    calls = 0

    async def failing_operation() -> dict:
        nonlocal calls
        calls += 1

        raise RuntimeError("simulated persistent failure")

    async def recovered_operation() -> dict:
        nonlocal calls
        calls += 1

        return {"recovered": True}

    try:
        ledger_1 = DatabaseReplayLedger(AsyncSessionLocal)
        runner_1 = DurableResilientStageRunner(ledger_1)

        failed = await runner_1.run(
            token,
            failing_operation,
            max_attempts=2,
        )

        assert failed.state == ExecutionState.FAILED
        assert failed.replayed is False
        assert failed.attempts == 2
        assert failed.error == "simulated persistent failure"
        assert calls == 2

        ledger_2 = DatabaseReplayLedger(AsyncSessionLocal)

        persisted = await ledger_2.get(token)

        assert persisted is not None
        assert persisted.state == ExecutionState.FAILED
        assert persisted.attempts == 2
        assert persisted.error == "simulated persistent failure"

        cleared = await ledger_2.clear_failed(token)

        assert cleared is True
        assert await ledger_2.get(token) is None

        runner_2 = DurableResilientStageRunner(ledger_2)

        recovered = await runner_2.run(
            token,
            recovered_operation,
        )

        assert recovered.state == ExecutionState.SUCCEEDED
        assert recovered.replayed is False
        assert recovered.attempts == 1
        assert recovered.value == {"recovered": True}
        assert calls == 3

        runner_3 = DurableResilientStageRunner(
            DatabaseReplayLedger(AsyncSessionLocal)
        )

        replayed = await runner_3.run(
            token,
            recovered_operation,
        )

        assert replayed.state == ExecutionState.SUCCEEDED
        assert replayed.replayed is True
        assert replayed.attempts == 1
        assert replayed.value == {"recovered": True}
        assert calls == 3

    finally:
        await _cleanup(token)


async def _test_concurrent_workers_execute_operation_once() -> None:
    unique_id = uuid.uuid4().hex

    token = ExecutionToken(
        tenant_id=f"tenant-{unique_id}",
        workflow_id="concurrent-maintenance",
        stage_name="maintenance-decision",
        payload={"machine_id": unique_id},
    )

    calls = 0
    operation_started = asyncio.Event()

    async def operation() -> dict:
        nonlocal calls
        calls += 1

        operation_started.set()

        await asyncio.sleep(0.2)

        return {
            "decision": "inspect",
            "machine_id": unique_id,
        }

    try:
        runner_1 = DurableResilientStageRunner(
            DatabaseReplayLedger(AsyncSessionLocal)
        )
        runner_2 = DurableResilientStageRunner(
            DatabaseReplayLedger(AsyncSessionLocal)
        )

        task_1 = asyncio.create_task(
            runner_1.run(
                token,
                operation,
                wait_timeout_seconds=5.0,
                poll_interval_seconds=0.02,
            )
        )

        await operation_started.wait()

        task_2 = asyncio.create_task(
            runner_2.run(
                token,
                operation,
                wait_timeout_seconds=5.0,
                poll_interval_seconds=0.02,
            )
        )

        result_1, result_2 = await asyncio.gather(
            task_1,
            task_2,
        )

        assert result_1.state == ExecutionState.SUCCEEDED
        assert result_2.state == ExecutionState.SUCCEEDED
        assert calls == 1

        assert {
            result_1.replayed,
            result_2.replayed,
        } == {False, True}

        expected_value = {
            "decision": "inspect",
            "machine_id": unique_id,
        }

        assert result_1.value == expected_value
        assert result_2.value == expected_value

        async with AsyncSessionLocal() as session:
            rows = await session.execute(
                select(RuntimeReplayExecution).where(
                    RuntimeReplayExecution.execution_key == token.key
                )
            )

            records = list(rows.scalars())

            assert len(records) == 1
            assert records[0].state == ExecutionState.SUCCEEDED.value
            assert records[0].attempts == 1

    finally:
        await _cleanup(token)


async def _test_expired_running_lease_is_taken_over() -> None:
    unique_id = uuid.uuid4().hex

    token = ExecutionToken(
        tenant_id=f"tenant-{unique_id}",
        workflow_id="crash-recovery",
        stage_name="failure-analysis",
        payload={"machine_id": unique_id},
    )

    crashed_owner = f"crashed-{uuid.uuid4().hex}"
    calls = 0

    async def recovered_operation() -> dict:
        nonlocal calls
        calls += 1

        return {
            "recovered": True,
            "machine_id": unique_id,
        }

    try:
        ledger = DatabaseReplayLedger(AsyncSessionLocal)

        claimed = await ledger.try_claim(
            token,
            lease_owner=crashed_owner,
            lease_seconds=30.0,
        )

        assert claimed is True

        # Simulate a process crash whose durable lease has expired.
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(RuntimeReplayExecution)
                .where(
                    RuntimeReplayExecution.execution_key == token.key
                )
                .values(
                    lease_expires_at=(
                        datetime.now(timezone.utc)
                        - timedelta(seconds=1)
                    )
                )
            )
            await session.commit()

        runner = DurableResilientStageRunner(
            DatabaseReplayLedger(AsyncSessionLocal)
        )

        result = await runner.run(
            token,
            recovered_operation,
            lease_seconds=1.0,
            heartbeat_interval_seconds=0.2,
            wait_timeout_seconds=3.0,
            poll_interval_seconds=0.02,
        )

        assert result.state == ExecutionState.SUCCEEDED
        assert result.replayed is False
        assert result.attempts == 1
        assert result.value == {
            "recovered": True,
            "machine_id": unique_id,
        }
        assert calls == 1

        record = await _get_record(token)

        assert record is not None
        assert record.state == ExecutionState.SUCCEEDED.value
        assert record.attempts == 1
        assert record.lease_owner is None
        assert record.lease_expires_at is None

    finally:
        await _cleanup(token)


async def _test_heartbeat_prevents_live_worker_takeover() -> None:
    unique_id = uuid.uuid4().hex

    token = ExecutionToken(
        tenant_id=f"tenant-{unique_id}",
        workflow_id="heartbeat-protection",
        stage_name="health-analysis",
        payload={"machine_id": unique_id},
    )

    calls = 0
    operation_started = asyncio.Event()

    async def operation() -> dict:
        nonlocal calls
        calls += 1

        operation_started.set()

        # Longer than the lease itself. The heartbeat must keep
        # the live worker's ownership valid.
        await asyncio.sleep(0.8)

        return {
            "healthy": True,
            "machine_id": unique_id,
        }

    try:
        runner_1 = DurableResilientStageRunner(
            DatabaseReplayLedger(AsyncSessionLocal)
        )
        runner_2 = DurableResilientStageRunner(
            DatabaseReplayLedger(AsyncSessionLocal)
        )

        task_1 = asyncio.create_task(
            runner_1.run(
                token,
                operation,
                lease_seconds=0.3,
                heartbeat_interval_seconds=0.05,
                wait_timeout_seconds=3.0,
                poll_interval_seconds=0.02,
            )
        )

        await operation_started.wait()

        # Wait beyond the original lease duration. Without heartbeat,
        # worker 2 would now be able to steal the claim.
        await asyncio.sleep(0.4)

        task_2 = asyncio.create_task(
            runner_2.run(
                token,
                operation,
                lease_seconds=0.3,
                heartbeat_interval_seconds=0.05,
                wait_timeout_seconds=3.0,
                poll_interval_seconds=0.02,
            )
        )

        result_1, result_2 = await asyncio.gather(
            task_1,
            task_2,
        )

        assert result_1.state == ExecutionState.SUCCEEDED
        assert result_2.state == ExecutionState.SUCCEEDED
        assert calls == 1

        assert result_1.replayed is False
        assert result_2.replayed is True

        record = await _get_record(token)

        assert record is not None
        assert record.state == ExecutionState.SUCCEEDED.value
        assert record.attempts == 1
        assert record.lease_owner is None
        assert record.lease_expires_at is None

    finally:
        await _cleanup(token)


async def _test_old_owner_cannot_overwrite_after_takeover() -> None:
    unique_id = uuid.uuid4().hex

    token = ExecutionToken(
        tenant_id=f"tenant-{unique_id}",
        workflow_id="ownership-fencing",
        stage_name="maintenance-decision",
        payload={"machine_id": unique_id},
    )

    old_owner = f"old-{uuid.uuid4().hex}"
    new_owner = f"new-{uuid.uuid4().hex}"

    try:
        ledger = DatabaseReplayLedger(AsyncSessionLocal)

        claimed = await ledger.try_claim(
            token,
            lease_owner=old_owner,
            lease_seconds=30.0,
        )

        assert claimed is True

        async with AsyncSessionLocal() as session:
            await session.execute(
                update(RuntimeReplayExecution)
                .where(
                    RuntimeReplayExecution.execution_key == token.key
                )
                .values(
                    lease_expires_at=(
                        datetime.now(timezone.utc)
                        - timedelta(seconds=1)
                    )
                )
            )
            await session.commit()

        taken_over = await ledger.try_takeover_stale_claim(
            token,
            lease_owner=new_owner,
            lease_seconds=5.0,
        )

        assert taken_over is True

        stale_result = StageExecutionResult(
            key=token.key,
            state=ExecutionState.SUCCEEDED,
            attempts=1,
            replayed=False,
            value={"owner": "old"},
        )

        ownership_error: RuntimeError | None = None

        try:
            await ledger.record_owned(
                token,
                stale_result,
                lease_owner=old_owner,
                terminal=True,
            )
        except RuntimeError as exc:
            ownership_error = exc

        assert ownership_error is not None
        assert (
            str(ownership_error)
            == "runtime replay lease ownership was lost"
        )

        record_after_old_owner = await _get_record(token)

        assert record_after_old_owner is not None
        assert record_after_old_owner.state == ExecutionState.RUNNING.value
        assert record_after_old_owner.lease_owner == new_owner

        valid_result = StageExecutionResult(
            key=token.key,
            state=ExecutionState.SUCCEEDED,
            attempts=1,
            replayed=False,
            value={"owner": "new"},
        )

        await ledger.record_owned(
            token,
            valid_result,
            lease_owner=new_owner,
            terminal=True,
        )

        final_record = await _get_record(token)

        assert final_record is not None
        assert final_record.state == ExecutionState.SUCCEEDED.value
        assert final_record.value == {"owner": "new"}
        assert final_record.lease_owner is None
        assert final_record.lease_expires_at is None

    finally:
        await _cleanup(token)


async def _run_runtime_resilience_tests() -> None:
    try:
        await _test_durable_replay_survives_runner_restart()
        await _test_durable_runner_retries_then_persists_success()
        await _test_failed_state_persists_and_can_be_recovered()
        await _test_concurrent_workers_execute_operation_once()
        await _test_expired_running_lease_is_taken_over()
        await _test_heartbeat_prevents_live_worker_takeover()
        await _test_old_owner_cannot_overwrite_after_takeover()
    finally:
        await engine.dispose()


def test_v371_runtime_resilience() -> None:
    asyncio.run(_run_runtime_resilience_tests())
