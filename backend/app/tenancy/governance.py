from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

class TenantAuditLog:
    def __init__(self) -> None: self._events: list[dict[str, Any]] = []
    def record(self, tenant_id: str, action: str, actor: str, **details: Any) -> None:
        self._events.append({"tenant_id": tenant_id, "action": action, "actor": actor, "details": details})
    def list(self, tenant_id: str) -> list[dict[str, Any]]:
        return [e for e in self._events if e["tenant_id"] == tenant_id]

@dataclass(slots=True)
class TenantQuota:
    max_integrations: int = 20
    max_dispatches: int = 1000

class QuotaManager:
    def __init__(self) -> None:
        self.quotas: dict[str, TenantQuota] = {}
        self.usage: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    def quota(self, tenant_id: str) -> TenantQuota: return self.quotas.get(tenant_id, TenantQuota())
    def consume_dispatch(self, tenant_id: str) -> None:
        if self.usage[tenant_id]["dispatches"] >= self.quota(tenant_id).max_dispatches: raise PermissionError("tenant dispatch quota exceeded")
        self.usage[tenant_id]["dispatches"] += 1
