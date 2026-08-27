import uuid

from pydantic import BaseModel, Field

from app.maintenance.counterfactual import CounterfactualEvidenceScope
from app.schemas.maintenance_verification import MaintenanceSnapshotResponse


class CounterfactualMaintenanceRequest(BaseModel):
    machine_type: str | None = None
    candidate_interventions: list[str] | None = None
    horizon_steps: int = Field(default=5, ge=1, le=30)
    event_limit: int = Field(default=100, ge=1, le=1000)
    library_limit: int = Field(default=500, ge=1, le=5000)
    history_limit: int = Field(default=1000, ge=1, le=5000)


class CounterfactualOutcomeResponse(BaseModel):
    intervention_type: str
    predicted_health_score: float
    predicted_risk_score: float
    predicted_deviation_score: float
    predicted_drift_score: float
    predicted_failure_match_score: float
    expected_recovery_score: float
    avoided_risk: float
    avoided_health_loss: float
    avoided_drift: float
    estimated_intervention_benefit: float
    confidence: float
    historical_support: int
    evidence_scope: CounterfactualEvidenceScope


class CounterfactualMaintenanceResponse(BaseModel):
    machine_id: uuid.UUID
    current: MaintenanceSnapshotResponse
    no_maintenance: CounterfactualOutcomeResponse
    candidates: list[CounterfactualOutcomeResponse]
    recommended_intervention: str | None
    recommendation_confidence: float
    horizon_steps: int
    evidence_note: str
