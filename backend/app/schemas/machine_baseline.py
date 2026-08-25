import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MachineBaselineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    machine_id: uuid.UUID
    baseline_version: str
    sample_count: int
    window_start: datetime
    window_end: datetime
    sensor_features: dict
    correlations: dict
    created_at: datetime
