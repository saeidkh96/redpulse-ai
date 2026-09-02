from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.security_v3.policy import AuthorizationContext, TenantPolicy


class MaintenanceIntentState(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class MaintenanceExecutionIntent:
    tenant_id: str
    machine_id: str
    action: str
    confidence: float
    risk_score: float


@dataclass(frozen=True, slots=True)
class MaintenanceApprovalPolicy:
    min_confidence: float = 0.75
    min_risk_score: float = 0.55
    human_approval_required: bool = True


class AutonomousMaintenanceCoordinator:
    def __init__(self, tenant_policy: TenantPolicy | None = None) -> None:
        self.tenant_policy = tenant_policy or TenantPolicy()

    def evaluate(
        self,
        intent: MaintenanceExecutionIntent,
        actor: AuthorizationContext,
        policy: MaintenanceApprovalPolicy | None = None,
    ) -> dict[str, object]:
        policy = policy or MaintenanceApprovalPolicy()
        if actor.tenant_id != intent.tenant_id:
            return {"state": MaintenanceIntentState.BLOCKED, "reason": "tenant_mismatch"}
        if intent.confidence < policy.min_confidence:
            return {"state": MaintenanceIntentState.BLOCKED, "reason": "insufficient_confidence"}
        if intent.risk_score < policy.min_risk_score:
            return {"state": MaintenanceIntentState.BLOCKED, "reason": "insufficient_risk"}
        if policy.human_approval_required and not self.tenant_policy.allowed(actor, "approve"):
            return {"state": MaintenanceIntentState.PROPOSED, "reason": "human_approval_required"}
        return {"state": MaintenanceIntentState.APPROVED, "reason": "policy_satisfied"}
