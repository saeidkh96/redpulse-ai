from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.health.scoring import MachineHealthState


class HealthScoreResponse(BaseModel):
    health_score: float
    risk_score: float
    state: MachineHealthState
    early_warning: bool
    components: dict[str, float]


class PersistenceResponse(BaseModel):
    score: float
    event_count: int
    deviation_count: int
    drift_count: int
    anomalous_count: int
    duration_seconds: float | None


class BestFailureMatchResponse(BaseModel):
    fingerprint_id: UUID
    machine_id: UUID
    failure_type: str
    machine_type: str | None
    title: str
    confidence: float | None
    failure_time: datetime | None
    overall_similarity: float


class MachineHealthResponse(BaseModel):
    machine_id: UUID

    health: HealthScoreResponse
    persistence: PersistenceResponse

    deviation_score: float
    drift_score: float
    failure_match_score: float

    best_failure_match: BestFailureMatchResponse | None
