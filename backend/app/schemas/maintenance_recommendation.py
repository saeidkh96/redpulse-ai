import uuid

from pydantic import BaseModel

from app.maintenance.decision import (
    MaintenanceActionType,
    MaintenancePriority,
)


class MaintenanceDecisionResponse(BaseModel):
    priority: MaintenancePriority
    action_type: MaintenanceActionType
    urgency_score: float
    recommended_action: str
    predicted_failure: str | None
    affected_signals: list[str]
    root_cause_hints: list[str]
    rationale: list[str]


class MaintenanceRecommendationResponse(BaseModel):
    machine_id: uuid.UUID
    decision: MaintenanceDecisionResponse
