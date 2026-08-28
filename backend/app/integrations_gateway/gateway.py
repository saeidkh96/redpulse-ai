from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol

@dataclass(slots=True)
class IntegrationEvent:
    event_type: str
    entity_id: str
    payload: dict[str, Any]

class IntegrationAdapter(Protocol):
    def send(self, event: IntegrationEvent) -> dict[str, Any]: ...

class IntegrationGateway:
    def __init__(self) -> None:
        self._adapters: dict[str, IntegrationAdapter] = {}

    def register(self, name: str, adapter: IntegrationAdapter) -> None:
        self._adapters[name] = adapter

    def dispatch(self, adapter: str, event: IntegrationEvent) -> dict[str, Any]:
        if adapter not in self._adapters:
            raise KeyError(f"unknown integration adapter: {adapter}")
        return self._adapters[adapter].send(event)

    def adapters(self) -> list[str]:
        return sorted(self._adapters)
