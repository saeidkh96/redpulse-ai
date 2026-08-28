from __future__ import annotations
from dataclasses import dataclass, field
from uuid import uuid4

@dataclass(slots=True)
class Tenant:
    name: str
    tenant_id: str = field(default_factory=lambda: str(uuid4()))
    active: bool = True

@dataclass(slots=True)
class TenantUser:
    tenant_id: str
    user_id: str
    roles: set[str] = field(default_factory=set)
