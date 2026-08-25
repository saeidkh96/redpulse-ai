import uuid
from datetime import datetime

from pydantic import BaseModel


class DriftTrendRead(BaseModel):
    slope: float
    normalized_slope: float
    cumulative_change: float
    monotonicity: float
    persistence: float


class DriftSignalRead(BaseModel):
    trend: DriftTrendRead
    score: float
    state: str


class DriftWindowRead(BaseModel):
    index: int
    window_start: datetime
    window_end: datetime
    sample_count: int
    deviation_score: float
    severity: str


class DriftAnalysisRead(BaseModel):
    machine_id: uuid.UUID
    baseline_version: str

    window_size: int
    window_count: int

    overall_score: float
    state: str

    windows: list[DriftWindowRead]
    signals: dict[str, DriftSignalRead]
