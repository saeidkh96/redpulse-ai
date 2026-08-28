from dataclasses import dataclass

@dataclass(frozen=True)
class AuthorizationContext:
    tenant_id: str
    roles: frozenset[str]

class TenantPolicy:
    PERMISSIONS = {
        "viewer": {"read"},
        "engineer": {"read", "investigate"},
        "maintainer": {"read", "investigate", "propose"},
        "approver": {"read", "approve"},
        "admin": {"*"},
    }

    def allowed(self, context: AuthorizationContext, permission: str) -> bool:
        granted = set()
        for role in context.roles:
            granted |= self.PERMISSIONS.get(role, set())
        return "*" in granted or permission in granted
