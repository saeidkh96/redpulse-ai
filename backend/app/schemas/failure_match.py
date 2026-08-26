from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FailureMatchScoreRead(BaseModel):
    overall_similarity: float
    sensor_similarity: float
    deviation_similarity: float
    drift_similarity: float
    correlation_similarity: float
    trajectory_similarity: float


class FailureMatchRead(BaseModel):
    fingerprint_id: UUID
    machine_id: UUID
    failure_type: str
    machine_type: str | None
    title: str
    confidence: float | None
    failure_time: datetime | None
    score: FailureMatchScoreRead


class FailureMatchingResponse(BaseModel):
    machine_id: UUID
    candidate_count: int
    match_count: int
    matches: list[FailureMatchRead]


class FailureMatchingRequest(BaseModel):
    failure_type: str | None = None
    machine_type: str | None = None

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
    )

    minimum_similarity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    event_limit: int = Field(
        default=100,
        ge=1,
        le=500,
    )

    library_limit: int = Field(
        default=500,
        ge=1,
        le=1000,
    )
