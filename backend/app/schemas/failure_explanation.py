import uuid

from pydantic import BaseModel

from app.explainability.failure_explanation import (
    EvidenceCategory,
)
from app.schemas.failure_prediction import (
    FailurePredictionResponse,
)


class ExplanationEvidenceResponse(BaseModel):
    category: EvidenceCategory
    name: str
    contribution: float
    value: float | None
    description: str


class RootCauseHintResponse(BaseModel):
    cause: str
    confidence: float
    supporting_evidence: list[str]


class FailureExplanationResponse(BaseModel):
    summary: str
    primary_driver: str | None
    evidence: list[ExplanationEvidenceResponse]
    root_cause_hints: list[RootCauseHintResponse]


class MachineFailureExplanationResponse(BaseModel):
    machine_id: uuid.UUID
    prediction: FailurePredictionResponse
    explanation: FailureExplanationResponse
