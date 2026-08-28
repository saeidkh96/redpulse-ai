from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

def utcnow() -> str: return datetime.now(timezone.utc).isoformat()

@dataclass(slots=True)
class ReadinessCheck:
    name: str
    ok: bool
    detail: str = ""

@dataclass(slots=True)
class ReadinessReport:
    version: str
    ready: bool
    checks: list[ReadinessCheck]
    generated_at: str = field(default_factory=utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
