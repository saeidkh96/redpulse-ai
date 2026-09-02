from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable

from app.runtime_v3.idempotency import idempotency_key


class ExecutionState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ExecutionToken:
    tenant_id: str
    workflow_id: str
    stage_name: str
    payload: dict[str, Any]

    @property
    def key(self) -> str:
        namespace = f"{self.tenant_id}:{self.workflow_id}:{self.stage_name}"
        return idempotency_key(namespace, self.payload)


@dataclass(frozen=True, slots=True)
class StageExecutionResult:
    key: str
    state: ExecutionState
    attempts: int
    replayed: bool
    value: Any = None
    error: str | None = None


@dataclass(slots=True)
class ReplayLedger:
    _results: dict[str, StageExecutionResult] = field(default_factory=dict)

    def get(self, key: str) -> StageExecutionResult | None:
        return self._results.get(key)

    def record(self, result: StageExecutionResult) -> None:
        self._results[result.key] = result

    def clear_failed(self, key: str) -> None:
        current = self._results.get(key)
        if current is not None and current.state == ExecutionState.FAILED:
            self._results.pop(key, None)


class TenantIsolationGuard:
    @staticmethod
    def validate(token: ExecutionToken, expected_tenant_id: str) -> None:
        if token.tenant_id != expected_tenant_id:
            raise PermissionError("cross-tenant workflow execution rejected")


class ResilientStageRunner:
    def __init__(self, ledger: ReplayLedger | None = None) -> None:
        self.ledger = ledger or ReplayLedger()

    def run(
        self,
        token: ExecutionToken,
        operation: Callable[[], Any],
        *,
        max_attempts: int = 3,
        retry_exceptions: tuple[type[BaseException], ...] = (Exception,),
    ) -> StageExecutionResult:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        existing = self.ledger.get(token.key)
        if existing is not None and existing.state == ExecutionState.SUCCEEDED:
            return StageExecutionResult(
                key=existing.key,
                state=existing.state,
                attempts=existing.attempts,
                replayed=True,
                value=existing.value,
                error=None,
            )

        attempts = 0
        last_error: BaseException | None = None
        while attempts < max_attempts:
            attempts += 1
            try:
                value = operation()
                result = StageExecutionResult(
                    key=token.key,
                    state=ExecutionState.SUCCEEDED,
                    attempts=attempts,
                    replayed=False,
                    value=value,
                )
                self.ledger.record(result)
                return result
            except retry_exceptions as exc:
                last_error = exc

        result = StageExecutionResult(
            key=token.key,
            state=ExecutionState.FAILED,
            attempts=attempts,
            replayed=False,
            error=str(last_error) if last_error is not None else "stage failed",
        )
        self.ledger.record(result)
        return result
