from typing import Any

from pydantic import BaseModel


class FailureRiskResponse(BaseModel):
    risk_score: float
    confidence: float
    level: str
    trend: str
    components: dict[str, float]


class FailurePredictionResponse(BaseModel):
    machine_id: str
    likely_failure_type: str | None
    likely_failure_title: str | None
    risk: FailureRiskResponse
    historical_match_confidence: float | None
    failure_match_score: float
    evidence: dict[str, Any]
