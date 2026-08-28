from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

class IntelligenceEventType(str, Enum):
    TELEMETRY_INGESTED = "telemetry_ingested"
    DEVIATION_DETECTED = "deviation_detected"
    DRIFT_DETECTED = "drift_detected"
    FAILURE_RISK_UPDATED = "failure_risk_updated"
    MAINTENANCE_PRIORITY_UPDATED = "maintenance_priority_updated"
    FLEET_WARNING_UPDATED = "fleet_warning_updated"
    PLANT_RISK_UPDATED = "plant_risk_updated"

@dataclass(frozen=True)
class TelemetryEvent:
    machine_id: str
    sensor: str
    value: float
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "machine_id": self.machine_id,
            "sensor": self.sensor,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

@dataclass(frozen=True)
class IntelligenceEvent:
    event_type: IntelligenceEventType
    entity_id: str
    score: float
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "event_type": self.event_type.value,
            "entity_id": self.entity_id,
            "score": self.score,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
        }
