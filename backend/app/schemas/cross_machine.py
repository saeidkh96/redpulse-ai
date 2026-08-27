import uuid

from pydantic import BaseModel, Field


class CrossMachineAnalysisRequest(BaseModel):
    peer_limit: int = Field(default=100, ge=1, le=1000)
    history_limit: int = Field(default=1000, ge=1, le=10000)


class CrossMachineInterventionEvidenceResponse(BaseModel):
    intervention_type: str
    peer_support: int
    weighted_success_score: float
    weighted_similarity: float
    evidence_score: float
    historical_support: int
    historical_confidence: float | None


class CrossMachineRecommendationResponse(BaseModel):
    target_machine_id: str
    machine_type: str | None
    evidence_scope: str
    peer_count: int
    interventions: list[CrossMachineInterventionEvidenceResponse]
    recommended_intervention: str | None
    recommendation_confidence: float


class CrossMachineAnalysisResponse(BaseModel):
    machine_id: uuid.UUID
    recommendation: CrossMachineRecommendationResponse
    evidence_note: str
