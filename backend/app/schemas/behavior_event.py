import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.behavior_event import (
    BehaviorEventType,
    BehaviorSeverity,
)


class BehaviorEventRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    machine_id: uuid.UUID

    event_type: BehaviorEventType
    severity: BehaviorSeverity

    score: float | None

    baseline_version: str | None

    window_start: datetime | None
    window_end: datetime | None

    summary: str | None

    evidence: dict

    created_at: datetime
