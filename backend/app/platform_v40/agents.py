from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from .intelligence import IntelligenceDecision


class WorkflowState(str, Enum):
    PROPOSED = "proposed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISPATCHED = "dispatched"
    VERIFIED = "verified"


@dataclass
class MaintenanceWorkflow:
    machine_id: str
    recommendation: str
    evidence: tuple[str, ...]
    risk: float
    id: str = field(default_factory=lambda: str(uuid4()))
    state: WorkflowState = WorkflowState.PROPOSED
    approved_by: str | None = None


class AgenticMaintenanceOrchestrator:
    def create(self, decision: IntelligenceDecision) -> MaintenanceWorkflow:
        if not decision.evidence:
            raise ValueError("agentic maintenance requires grounded evidence")
        workflow = MaintenanceWorkflow(
            machine_id=decision.machine_id,
            recommendation=f"Inspect machine with {decision.maintenance_priority} priority",
            evidence=decision.evidence,
            risk=decision.failure_risk,
        )
        workflow.state = WorkflowState.AWAITING_APPROVAL
        return workflow

    def approve(self, workflow: MaintenanceWorkflow, approver: str) -> MaintenanceWorkflow:
        if workflow.state is not WorkflowState.AWAITING_APPROVAL:
            raise ValueError("workflow is not awaiting approval")
        if not approver:
            raise ValueError("approver is required")
        workflow.approved_by = approver
        workflow.state = WorkflowState.APPROVED
        return workflow

    def reject(self, workflow: MaintenanceWorkflow) -> MaintenanceWorkflow:
        if workflow.state is not WorkflowState.AWAITING_APPROVAL:
            raise ValueError("workflow is not awaiting approval")
        workflow.state = WorkflowState.REJECTED
        return workflow

    def mark_dispatched(self, workflow: MaintenanceWorkflow) -> MaintenanceWorkflow:
        if workflow.state is not WorkflowState.APPROVED:
            raise PermissionError("human approval is required before dispatch")
        workflow.state = WorkflowState.DISPATCHED
        return workflow

    def verify(self, workflow: MaintenanceWorkflow, recovered: bool) -> MaintenanceWorkflow:
        if workflow.state is not WorkflowState.DISPATCHED:
            raise ValueError("only dispatched workflows can be verified")
        if recovered:
            workflow.state = WorkflowState.VERIFIED
        return workflow
