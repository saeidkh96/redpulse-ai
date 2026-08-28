from dataclasses import dataclass
from enum import Enum

class DataTier(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"

@dataclass(frozen=True)
class TelemetryStoragePlan:
    hot_store: str = "timescaledb"
    warm_store: str = "parquet"
    cold_store: str = "object_storage"

@dataclass(frozen=True)
class AnalyticsJob:
    name: str
    input_path: str
    output_path: str
    engine: str = "spark"

@dataclass(frozen=True)
class AnalyticsJobResult:
    job_name: str
    status: str
    output_path: str
    metadata: dict
