from __future__ import annotations
from .models import Tenant, TenantUser
from .security import TenantApiKeys, TenantRBAC
from .governance import QuotaManager, TenantAuditLog

class MultiTenantPlatform:
    def __init__(self) -> None:
        self.tenants: dict[str, Tenant] = {}
        self.users: dict[tuple[str, str], TenantUser] = {}
        self.api_keys, self.quotas, self.audit = TenantApiKeys(), QuotaManager(), TenantAuditLog()

    def create_tenant(self, name: str) -> Tenant:
        tenant = Tenant(name=name); self.tenants[tenant.tenant_id] = tenant; return tenant
    def add_user(self, tenant_id: str, user_id: str, roles: set[str]) -> TenantUser:
        if tenant_id not in self.tenants: raise KeyError("tenant not found")
        user = TenantUser(tenant_id, user_id, roles); self.users[(tenant_id, user_id)] = user; return user
    def authorize(self, tenant_id: str, user_id: str, permission: str) -> bool:
        user = self.users.get((tenant_id, user_id)); return bool(user and TenantRBAC.allowed(user.roles, permission))
