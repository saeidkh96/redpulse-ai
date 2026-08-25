from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SensorReading:
    timestamp: datetime
    sensor: str
    value: float
    unit: str


@dataclass(frozen=True)
class MachineSnapshot:
    machine_id: str
    timestamp: datetime
    readings: list[SensorReading]
