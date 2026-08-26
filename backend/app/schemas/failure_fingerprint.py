from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FailureFingerprintCreate(BaseModel):
    failure_type: str = Field(
        min_length=1,
        max_length=150,
    )
    machine_type: str | None = Field(
        default=None,
        max_length=100,
    )
    title: str = Field(
        min_length=1,
        max_length=255,
    )
    description: str | None = None
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    failure_time: datetime | None = None


class FailureFingerprintResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    machine_id: UUID

    failure_type: str
    machine_type: str | None

    title: str
    description: str | None
    confidence: float | None

    baseline_version: str | None

    trajectory_start: datetime | None
    trajectory_end: datetime | None
    failure_time: datetime | None

    dominant_sensors: list
    deviation_signature: dict
    drift_signature: dict
    correlation_signature: dict
    trajectory_summary: dict
    evidence: dict

    created_at: datetime
    updated_at: datetime


class FailureFingerprintListResponse(BaseModel):
    value: list[FailureFingerprintResponse]
    Count: int
