from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Protocol
from .models import AutomationEvent
from .reliability import ReliableDispatcher

class Adapter(Protocol):
    def send(self, event: AutomationEvent) -> dict[str, Any]: ...

@dataclass(slots=True)
class IntegrationRegistration:
    name: str
    provider: str
    tenant_id: str = "default"
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

class AutomationControlPlane:
    def __init__(self) -> None:
        self._adapters: dict[tuple[str, str], Adapter] = {}
        self._registrations: dict[tuple[str, str], IntegrationRegistration] = {}
        self.dispatcher = ReliableDispatcher()
        self.audit: list[dict[str, Any]] = []

    def register(self, registration: IntegrationRegistration, adapter: Adapter) -> None:
        key = (registration.tenant_id, registration.name)
        self._registrations[key], self._adapters[key] = registration, adapter

    def list(self, tenant_id: str) -> list[IntegrationRegistration]:
        return [r for (t, _), r in self._registrations.items() if t == tenant_id]

    def dispatch(self, name: str, event: AutomationEvent) -> dict[str, Any]:
        key = (event.tenant_id, name)
        registration = self._registrations.get(key)
        if registration is None: raise KeyError(f"integration not found: {name}")
        if not registration.enabled: raise PermissionError(f"integration disabled: {name}")
        result = self.dispatcher.execute(f"{event.tenant_id}:{name}:{event.event_id}", lambda: self._adapters[key].send(event))
        self.audit.append({"tenant_id": event.tenant_id, "integration": name, "event_id": event.event_id, "ok": result.get("ok", False)})
        return result
