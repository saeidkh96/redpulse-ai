import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TelemetryCreate(BaseModel):
    machine_id: uuid.UUID
    timestamp: datetime
    sensor: str = Field(min_length=1, max_length=100)
    value: float
    unit: str | None = Field(default=None, max_length=50)

    @field_validator("sensor")
    @classmethod
    def normalize_sensor(cls, value: str) -> str:
        return value.strip().lower()


class TelemetryBatchCreate(BaseModel):
    measurements: list[TelemetryCreate] = Field(
        min_length=1,
        max_length=1000,
    )


class TelemetryRead(TelemetryCreate):
    pass


class TelemetryBatchResult(BaseModel):
    inserted: int
