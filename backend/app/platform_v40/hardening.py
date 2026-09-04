from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import monotonic
from typing import Callable
from uuid import uuid4


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass(frozen=True)
class RuntimeProfile:
    environment: Environment
    debug: bool = False
    strict_dependencies: bool = True
    graceful_shutdown_seconds: float = 30.0

    def validate(self) -> None:
        if self.environment is Environment.PRODUCTION and self.debug:
            raise ValueError("debug must be disabled in production")
        if self.graceful_shutdown_seconds <= 0:
            raise ValueError("graceful_shutdown_seconds must be positive")


class ErrorCode(str, Enum):
    VALIDATION = "validation_error"
    DEPENDENCY = "dependency_unavailable"
    CONFLICT = "conflict"
    FORBIDDEN = "forbidden"
    RATE_LIMITED = "rate_limited"
    INTERNAL = "internal_error"


@dataclass(frozen=True)
class PlatformError(Exception):
    code: ErrorCode
    message: str
    retryable: bool = False
    details: dict = field(default_factory=dict)

    def as_contract(self, correlation_id: str) -> dict:
        return {
            "error": {"code": self.code.value, "message": self.message, "retryable": self.retryable, "details": self.details},
            "correlation_id": correlation_id,
        }


@dataclass(frozen=True)
class RequestContext:
    correlation_id: str
    tenant_id: str | None = None

    @classmethod
    def create(cls, tenant_id: str | None = None, correlation_id: str | None = None) -> "RequestContext":
        return cls(correlation_id or str(uuid4()), tenant_id)


@dataclass
class DependencyProbe:
    checks: dict[str, Callable[[], bool]] = field(default_factory=dict)

    def register(self, name: str, check: Callable[[], bool]) -> None:
        self.checks[name] = check

    def readiness(self) -> dict[str, object]:
        results: dict[str, bool] = {}
        for name, check in self.checks.items():
            try:
                results[name] = bool(check())
            except Exception:
                results[name] = False
        return {"ready": all(results.values()) if results else True, "dependencies": results}


class IdempotencyRegistry:
    def __init__(self) -> None:
        self._results: dict[str, object] = {}

    def execute_once(self, key: str, operation: Callable[[], object]) -> dict[str, object]:
        if not key:
            raise ValueError("idempotency key is required")
        if key in self._results:
            return {"duplicate": True, "value": self._results[key]}
        value = operation()
        self._results[key] = value
        return {"duplicate": False, "value": value}


@dataclass
class LifecycleCoordinator:
    started_at: float | None = None
    shutting_down: bool = False

    def start(self) -> None:
        self.started_at = monotonic()
        self.shutting_down = False

    def begin_shutdown(self) -> None:
        self.shutting_down = True

    @property
    def uptime_seconds(self) -> float:
        return 0.0 if self.started_at is None else max(0.0, monotonic() - self.started_at)
