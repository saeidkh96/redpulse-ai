from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class Identity:
    subject: str
    tenant_id: str
    roles: frozenset[str]


@dataclass(frozen=True)
class Policy:
    action: str
    allowed_roles: frozenset[str]


class PolicyEngine:
    def authorize(self, identity: Identity, target_tenant: str, policy: Policy) -> None:
        if identity.tenant_id != target_tenant:
            raise PermissionError("cross-tenant access rejected")
        if not identity.roles.intersection(policy.allowed_roles):
            raise PermissionError("principal is not authorized for action")


@dataclass(frozen=True)
class AuditEvent:
    actor: str
    tenant_id: str
    action: str
    resource: str
    outcome: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLog:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def record(self, event: AuditEvent) -> None:
        self.events.append(event)

    def for_tenant(self, tenant_id: str) -> list[AuditEvent]:
        return [event for event in self.events if event.tenant_id == tenant_id]


class FixedWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        if limit < 1 or window_seconds < 1:
            raise ValueError("limit and window_seconds must be positive")
        self.limit = limit
        self.window = timedelta(seconds=window_seconds)
        self._state: dict[str, tuple[datetime, int]] = {}

    def allow(self, key: str, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        start, count = self._state.get(key, (now, 0))
        if now - start >= self.window:
            start, count = now, 0
        count += 1
        self._state[key] = (start, count)
        return count <= self.limit
