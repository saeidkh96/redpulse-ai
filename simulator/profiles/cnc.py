from dataclasses import dataclass


@dataclass(frozen=True)
class CNCProfile:
    idle_rpm: float = 0.0
    normal_rpm: float = 4200.0

    idle_load: float = 5.0
    normal_load: float = 65.0

    base_temperature: float = 42.0
    base_current: float = 1.2
    base_vibration: float = 0.35

    temperature_per_load: float = 0.34
    current_per_load: float = 0.105
    vibration_per_rpm: float = 0.00043

    rpm_noise: float = 70.0
    load_noise: float = 3.0
    temperature_noise: float = 0.7
    current_noise: float = 0.18
    vibration_noise: float = 0.08
