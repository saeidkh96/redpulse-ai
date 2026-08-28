from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass(slots=True)
class AutomationEvent:
    event_type: str
    entity_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    tenant_id: str = "default"
    event_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id, "event_type": self.event_type,
            "entity_id": self.entity_id, "tenant_id": self.tenant_id,
            "payload": self.payload, "created_at": self.created_at,
        }
