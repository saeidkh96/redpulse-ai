from dataclasses import dataclass

@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    roles: frozenset[str]

class RBAC:
    PERMISSIONS = {
        "viewer": {"read"},
        "engineer": {"read", "investigate"},
        "maintainer": {"read", "investigate", "propose_maintenance"},
        "approver": {"read", "approve_maintenance"},
        "admin": {"*"},
    }

    def allowed(self, principal: Principal, permission: str) -> bool:
        granted = set()
        for role in principal.roles:
            granted |= self.PERMISSIONS.get(role, set())
        return "*" in granted or permission in granted
