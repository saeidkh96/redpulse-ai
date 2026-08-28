from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class MachineContext:
    machine_id: str
    machine_dna: dict[str, Any] = field(default_factory=dict)
    telemetry: dict[str, Any] = field(default_factory=dict)
    health: dict[str, Any] = field(default_factory=dict)
    failure_risk: dict[str, Any] = field(default_factory=dict)
    maintenance_history: list[dict[str, Any]] = field(default_factory=list)

    def as_prompt_context(self) -> str:
        return (
            f"machine_id={self.machine_id}\n"
            f"machine_dna={self.machine_dna}\n"
            f"telemetry={self.telemetry}\n"
            f"health={self.health}\n"
            f"failure_risk={self.failure_risk}\n"
            f"maintenance_history={self.maintenance_history}"
        )
