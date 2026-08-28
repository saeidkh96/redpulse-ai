from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time
import uuid

class RuntimeStatus(str, Enum):
    PENDING = "pending"
    WAITING_APPROVAL = "waiting_approval"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DEAD = "dead"

@dataclass(slots=True)
class RuntimeRecord:
    record_id: str
    tenant_id: str
    kind: str
    status: RuntimeStatus
    payload: dict[str, Any] = field(default_factory=dict)
    attempts: int = 0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    @classmethod
    def create(cls, tenant_id: str, kind: str, payload: dict[str, Any] | None = None) -> "RuntimeRecord":
        return cls(
            record_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            kind=kind,
            status=RuntimeStatus.PENDING,
            payload=payload or {},
        )
