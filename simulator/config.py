from dataclasses import dataclass


@dataclass(frozen=True)
class SimulatorConfig:
    machine_id: str
    seed: int = 42
    sampling_interval_seconds: float = 1.0
