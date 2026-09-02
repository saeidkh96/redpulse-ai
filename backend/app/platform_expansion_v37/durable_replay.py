from __future__ import annotations

import asyncio
import contextlib
import time
import uuid
from typing import Any, Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.platform_expansion_v37.resilience import (
    ExecutionState,
    ExecutionToken,
    StageExecutionResult,
)
from app.repositories.runtime_replay_execution import (
    RuntimeReplayExecutionRepository,
    runtime_replay_execution_repository,
)


class DatabaseReplayLedger:
    """PostgreSQL-backed replay ledger for restart-safe stage execution."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        repository: RuntimeReplayExecutionRepository | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.repository = (
            repository or runtime_replay_execution_repository
        )

    @staticmethod
    def _to_result(
        record: Any,
        *,
        replayed: bool,
    ) -> StageExecutionResult:
        return StageExecutionResult(
            key=record.execution_key,
            state=ExecutionState(record.state),
            attempts=record.attempts,
            replayed=replayed,
            value=record.value,
            error=record.error,
        )

    async def get(
        self,
        token: ExecutionToken,
    ) -> StageExecutionResult | None:
        async with self.session_factory() as session:
            record = await self.repository.get(
                session,
                token.key,
            )

            if record is None:
                return None

            if record.tenant_id != token.tenant_id:
                raise PermissionError(
                    "cross-tenant replay execution rejected"
                )

            return self._to_result(
                record,
                replayed=False,
            )

    async def try_claim(
        self,
        token: ExecutionToken,
        *,
        lease_owner: str,
        lease_seconds: float,
    ) -> bool:
        async with self.session_factory() as session:
            return await self.repository.try_claim(
                session,
                execution_key=token.key,
                tenant_id=token.tenant_id,
                workflow_id=token.workflow_id,
                stage_name=token.stage_name,
                lease_owner=lease_owner,
                lease_seconds=lease_seconds,
            )

    async def try_takeover_stale_claim(
        self,
        token: ExecutionToken,
        *,
        lease_owner: str,
        lease_seconds: float,
    ) -> bool:
        async with self.session_factory() as session:
            return await self.repository.try_takeover_stale_claim(
                session,
                execution_key=token.key,
                tenant_id=token.tenant_id,
                lease_owner=lease_owner,
                lease_seconds=lease_seconds,
            )

    async def renew_lease(
        self,
        token: ExecutionToken,
        *,
        lease_owner: str,
        lease_seconds: float,
    ) -> bool:
        async with self.session_factory() as session:
            return await self.repository.renew_lease(
                session,
                execution_key=token.key,
                tenant_id=token.tenant_id,
                lease_owner=lease_owner,
                lease_seconds=lease_seconds,
            )

    async def record_owned(
        self,
        token: ExecutionToken,
        result: StageExecutionResult,
        *,
        lease_owner: str,
        lease_seconds: float | None = None,
        terminal: bool = False,
    ) -> None:
        value = result.value

        if value is not None and not isinstance(value, dict):
            value = {"result": value}

        async with self.session_factory() as session:
            await self.repository.save_owned(
                session,
                execution_key=result.key,
                tenant_id=token.tenant_id,
                workflow_id=token.workflow_id,
                stage_name=token.stage_name,
                lease_owner=lease_owner,
                state=result.state.value,
                attempts=result.attempts,
                value=value,
                error=result.error,
                lease_seconds=lease_seconds,
                terminal=terminal,
            )

    async def clear_failed(
        self,
        token: ExecutionToken,
    ) -> bool:
        async with self.session_factory() as session:
            return await self.repository.clear_failed(
                session,
                token.key,
            )

    async def wait_for_terminal_or_takeover(
        self,
        token: ExecutionToken,
        *,
        lease_owner: str,
        lease_seconds: float,
        timeout_seconds: float,
        poll_interval_seconds: float,
    ) -> StageExecutionResult | None:
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than 0"
            )

        if poll_interval_seconds <= 0:
            raise ValueError(
                "poll_interval_seconds must be greater than 0"
            )

        deadline = time.monotonic() + timeout_seconds

        while time.monotonic() < deadline:
            result = await self.get(token)

            if result is None:
                claimed = await self.try_claim(
                    token,
                    lease_owner=lease_owner,
                    lease_seconds=lease_seconds,
                )

                if claimed:
                    return None

            elif result.state in {
                ExecutionState.SUCCEEDED,
                ExecutionState.FAILED,
            }:
                return StageExecutionResult(
                    key=result.key,
                    state=result.state,
                    attempts=result.attempts,
                    replayed=True,
                    value=result.value,
                    error=result.error,
                )

            elif result.state == ExecutionState.RUNNING:
                taken_over = await self.try_takeover_stale_claim(
                    token,
                    lease_owner=lease_owner,
                    lease_seconds=lease_seconds,
                )

                if taken_over:
                    return None

            await asyncio.sleep(poll_interval_seconds)

        raise TimeoutError(
            "timed out waiting for execution or stale lease takeover"
        )


class DurableResilientStageRunner:
    """
    Restart-safe resilient stage runner backed by PostgreSQL.

    Workers use durable claims with expiring leases. The active worker
    renews its lease while an operation is running. If a worker stops
    renewing the lease, another worker can atomically take over after
    expiration.

    Database state transitions are ownership-checked so a worker that
    loses its lease cannot overwrite the execution state.
    """

    def __init__(
        self,
        ledger: DatabaseReplayLedger,
    ) -> None:
        self.ledger = ledger

    async def _heartbeat(
        self,
        token: ExecutionToken,
        *,
        lease_owner: str,
        lease_seconds: float,
        heartbeat_interval_seconds: float,
        lease_lost: asyncio.Event,
    ) -> None:
        try:
            while True:
                await asyncio.sleep(heartbeat_interval_seconds)

                renewed = await self.ledger.renew_lease(
                    token,
                    lease_owner=lease_owner,
                    lease_seconds=lease_seconds,
                )

                if not renewed:
                    lease_lost.set()
                    return

        except asyncio.CancelledError:
            raise

    async def _execute_as_owner(
        self,
        token: ExecutionToken,
        operation: Callable[[], Awaitable[Any]],
        *,
        lease_owner: str,
        lease_seconds: float,
        heartbeat_interval_seconds: float,
        max_attempts: int,
        retry_exceptions: tuple[type[BaseException], ...],
    ) -> StageExecutionResult:
        persisted = await self.ledger.get(token)

        attempts = (
            persisted.attempts
            if persisted is not None
            else 0
        )

        last_error: BaseException | None = None

        while attempts < max_attempts:
            attempts += 1

            running = StageExecutionResult(
                key=token.key,
                state=ExecutionState.RUNNING,
                attempts=attempts,
                replayed=False,
            )

            await self.ledger.record_owned(
                token,
                running,
                lease_owner=lease_owner,
                lease_seconds=lease_seconds,
                terminal=False,
            )

            lease_lost = asyncio.Event()

            heartbeat_task = asyncio.create_task(
                self._heartbeat(
                    token,
                    lease_owner=lease_owner,
                    lease_seconds=lease_seconds,
                    heartbeat_interval_seconds=(
                        heartbeat_interval_seconds
                    ),
                    lease_lost=lease_lost,
                )
            )

            try:
                value = await operation()

            except retry_exceptions as exc:
                last_error = exc

                heartbeat_task.cancel()

                with contextlib.suppress(asyncio.CancelledError):
                    await heartbeat_task

                if lease_lost.is_set():
                    raise RuntimeError(
                        "runtime replay lease ownership was lost"
                    )

                continue

            except BaseException:
                heartbeat_task.cancel()

                with contextlib.suppress(asyncio.CancelledError):
                    await heartbeat_task

                raise

            heartbeat_task.cancel()

            with contextlib.suppress(asyncio.CancelledError):
                await heartbeat_task

            if lease_lost.is_set():
                raise RuntimeError(
                    "runtime replay lease ownership was lost"
                )

            result = StageExecutionResult(
                key=token.key,
                state=ExecutionState.SUCCEEDED,
                attempts=attempts,
                replayed=False,
                value=value,
            )

            await self.ledger.record_owned(
                token,
                result,
                lease_owner=lease_owner,
                terminal=True,
            )

            return result

        result = StageExecutionResult(
            key=token.key,
            state=ExecutionState.FAILED,
            attempts=attempts,
            replayed=False,
            error=(
                str(last_error)
                if last_error is not None
                else "stage failed"
            ),
        )

        await self.ledger.record_owned(
            token,
            result,
            lease_owner=lease_owner,
            terminal=True,
        )

        return result

    async def run(
        self,
        token: ExecutionToken,
        operation: Callable[[], Awaitable[Any]],
        *,
        max_attempts: int = 3,
        retry_exceptions: tuple[type[BaseException], ...] = (
            Exception,
        ),
        wait_timeout_seconds: float = 10.0,
        poll_interval_seconds: float = 0.05,
        lease_seconds: float = 5.0,
        heartbeat_interval_seconds: float | None = None,
    ) -> StageExecutionResult:
        if max_attempts < 1:
            raise ValueError(
                "max_attempts must be at least 1"
            )

        if lease_seconds <= 0:
            raise ValueError(
                "lease_seconds must be greater than 0"
            )

        if heartbeat_interval_seconds is None:
            heartbeat_interval_seconds = lease_seconds / 3

        if heartbeat_interval_seconds <= 0:
            raise ValueError(
                "heartbeat_interval_seconds must be greater than 0"
            )

        if heartbeat_interval_seconds >= lease_seconds:
            raise ValueError(
                "heartbeat_interval_seconds must be less than "
                "lease_seconds"
            )

        lease_owner = uuid.uuid4().hex

        existing = await self.ledger.get(token)

        if existing is not None:
            if existing.state == ExecutionState.SUCCEEDED:
                return StageExecutionResult(
                    key=existing.key,
                    state=existing.state,
                    attempts=existing.attempts,
                    replayed=True,
                    value=existing.value,
                    error=None,
                )

            if existing.state == ExecutionState.FAILED:
                return StageExecutionResult(
                    key=existing.key,
                    state=existing.state,
                    attempts=existing.attempts,
                    replayed=True,
                    value=existing.value,
                    error=existing.error,
                )

        claimed = await self.ledger.try_claim(
            token,
            lease_owner=lease_owner,
            lease_seconds=lease_seconds,
        )

        if not claimed:
            taken_over = await self.ledger.try_takeover_stale_claim(
                token,
                lease_owner=lease_owner,
                lease_seconds=lease_seconds,
            )

            if not taken_over:
                terminal = await self.ledger.wait_for_terminal_or_takeover(
                    token,
                    lease_owner=lease_owner,
                    lease_seconds=lease_seconds,
                    timeout_seconds=wait_timeout_seconds,
                    poll_interval_seconds=poll_interval_seconds,
                )

                if terminal is not None:
                    return terminal

        return await self._execute_as_owner(
            token,
            operation,
            lease_owner=lease_owner,
            lease_seconds=lease_seconds,
            heartbeat_interval_seconds=heartbeat_interval_seconds,
            max_attempts=max_attempts,
            retry_exceptions=retry_exceptions,
        )
