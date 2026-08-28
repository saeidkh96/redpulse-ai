from __future__ import annotations
import hashlib, secrets
from dataclasses import dataclass

ROLE_PERMISSIONS = {
    "viewer": {"read"},
    "operator": {"read", "dispatch"},
    "admin": {"read", "dispatch", "manage_integrations", "manage_tenant"},
}

class TenantRBAC:
    @staticmethod
    def allowed(roles: set[str], permission: str) -> bool:
        return any(permission in ROLE_PERMISSIONS.get(role, set()) for role in roles)

@dataclass(slots=True)
class ApiKeyRecord:
    tenant_id: str
    key_hash: str
    label: str

class TenantApiKeys:
    def __init__(self) -> None: self._records: list[ApiKeyRecord] = []
    def issue(self, tenant_id: str, label: str = "default") -> str:
        raw = "rp_" + secrets.token_urlsafe(24)
        self._records.append(ApiKeyRecord(tenant_id, hashlib.sha256(raw.encode()).hexdigest(), label))
        return raw
    def resolve(self, raw: str) -> str | None:
        digest = hashlib.sha256(raw.encode()).hexdigest()
        return next((r.tenant_id for r in self._records if secrets.compare_digest(r.key_hash, digest)), None)
