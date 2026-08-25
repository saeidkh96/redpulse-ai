import uuid
from datetime import datetime

from pydantic import BaseModel


class SensorDeviationRead(BaseModel):
    mean_zscore: float
    std_ratio: float
    score: float


class CorrelationDeviationRead(BaseModel):
    baseline: float
    current: float
    delta: float
    score: float


class DeviationAnalysisRead(BaseModel):
    machine_id: uuid.UUID
    baseline_version: str

    sample_count: int
    window_start: datetime
    window_end: datetime

    overall_score: float
    severity: str

    sensor_deviations: dict[
        str,
        SensorDeviationRead,
    ]

    correlation_shifts: dict[
        str,
        CorrelationDeviationRead,
    ]
