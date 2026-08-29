from dataclasses import dataclass, field

@dataclass(frozen=True)
class GovernancePolicy:
    resource: str
    principal: str
    permissions: tuple[str, ...]
    tenant_id: str

@dataclass(frozen=True)
class LineageEdge:
    source: str
    target: str
    transformation: str

@dataclass
class GovernanceService:
    policies: list[GovernancePolicy] = field(default_factory=list)
    lineage: list[LineageEdge] = field(default_factory=list)

    def grant(self, resource: str, principal: str, permissions: list[str], tenant_id: str) -> GovernancePolicy:
        policy = GovernancePolicy(resource, principal, tuple(sorted(set(permissions))), tenant_id)
        self.policies.append(policy)
        return policy

    def can_access(self, resource: str, principal: str, permission: str, tenant_id: str) -> bool:
        return any(
            p.resource == resource and p.principal == principal
            and p.tenant_id == tenant_id and permission in p.permissions
            for p in self.policies
        )

    def add_lineage(self, source: str, target: str, transformation: str) -> LineageEdge:
        edge = LineageEdge(source, target, transformation)
        self.lineage.append(edge)
        return edge

governance_service = GovernanceService()
