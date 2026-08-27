import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.maintenance.outcome import LearnedOutcomeState
from app.schemas.maintenance_verification import (
    MaintenanceSnapshotRequest,
    MaintenanceSnapshotResponse,
    MaintenanceVerificationResponse,
)


class MaintenanceInterventionCreate(BaseModel):
    machine_type: str | None = None
    intervention_type: str = Field(min_length=1, max_length=150)
    failure_prediction: dict = Field(default_factory=dict)
    recommendation: dict = Field(default_factory=dict)
    technician_notes: str | None = None
    before_snapshot: MaintenanceSnapshotRequest
    started_at: datetime | None = None


class MaintenanceInterventionUpdate(BaseModel):
    technician_notes: str | None = None
    status: str | None = None
    started_at: datetime | None = None


class MaintenanceInterventionResponse(BaseModel):
    id: uuid.UUID
    machine_id: uuid.UUID
    machine_type: str | None
    intervention_type: str
    status: str
    failure_prediction: dict
    recommendation: dict
    technician_notes: str | None
    before_snapshot: dict
    after_snapshot: dict
    verification_result: dict
    outcome_label: str | None
    outcome_score: float | None
    outcome_evidence: dict
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MaintenanceCompletionResponse(BaseModel):
    intervention: MaintenanceInterventionResponse
    before: MaintenanceSnapshotResponse
    after: MaintenanceSnapshotResponse
    verification: MaintenanceVerificationResponse


class LearnedInterventionProfileResponse(BaseModel):
    intervention_type: str
    sample_count: int
    average_recovery_score: float
    average_risk_reduction: float
    average_drift_reduction: float
    average_health_improvement: float
    success_rate: float
    confidence: float
    state: LearnedOutcomeState
