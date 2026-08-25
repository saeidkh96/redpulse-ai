from dataclasses import dataclass


@dataclass(frozen=True)
class DegradationProfile:
    vibration_multiplier: float = 1.0
    vibration_offset: float = 0.0

    temperature_offset: float = 0.0

    current_multiplier: float = 1.0
    current_offset: float = 0.0

    rpm_vibration_coupling_multiplier: float = 1.0


NORMAL_DEGRADATION = DegradationProfile()


MILD_DEGRADATION = DegradationProfile(
    vibration_multiplier=1.08,
    vibration_offset=0.08,
    temperature_offset=1.5,
    current_multiplier=1.03,
    rpm_vibration_coupling_multiplier=1.10,
)


MODERATE_DEGRADATION = DegradationProfile(
    vibration_multiplier=1.25,
    vibration_offset=0.20,
    temperature_offset=4.0,
    current_multiplier=1.08,
    current_offset=0.20,
    rpm_vibration_coupling_multiplier=1.35,
)


SEVERE_DEGRADATION = DegradationProfile(
    vibration_multiplier=1.60,
    vibration_offset=0.45,
    temperature_offset=8.0,
    current_multiplier=1.18,
    current_offset=0.50,
    rpm_vibration_coupling_multiplier=1.80,
)
