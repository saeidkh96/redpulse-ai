import random
from datetime import datetime, timezone

from simulator.config import SimulatorConfig
from simulator.models import MachineSnapshot, SensorReading
from simulator.profiles.cnc import CNCProfile
from simulator.profiles.degradation import (
    DegradationProfile,
    NORMAL_DEGRADATION,
)


class CNCSimulator:
    def __init__(
        self,
        config: SimulatorConfig,
        profile: CNCProfile | None = None,
        degradation: DegradationProfile | None = None,
    ) -> None:
        self.config = config
        self.profile = profile or CNCProfile()
        self.degradation = (
            degradation or NORMAL_DEGRADATION
        )

        self.random = random.Random(
            config.seed
        )

    def generate_snapshot(
        self,
        timestamp: datetime | None = None,
    ) -> MachineSnapshot:
        timestamp = (
            timestamp
            or datetime.now(timezone.utc)
        )

        load = self.random.gauss(
            self.profile.normal_load,
            self.profile.load_noise,
        )

        load = max(
            0.0,
            min(100.0, load),
        )

        rpm = self.random.gauss(
            self.profile.normal_rpm,
            self.profile.rpm_noise,
        )

        rpm = max(
            0.0,
            rpm,
        )

        temperature = (
            self.profile.base_temperature
            + load
            * self.profile.temperature_per_load
            + self.random.gauss(
                0.0,
                self.profile.temperature_noise,
            )
        )

        temperature += (
            self.degradation.temperature_offset
        )

        current = (
            self.profile.base_current
            + load
            * self.profile.current_per_load
            + self.random.gauss(
                0.0,
                self.profile.current_noise,
            )
        )

        current = (
            current
            * self.degradation.current_multiplier
            + self.degradation.current_offset
        )

        vibration = (
            self.profile.base_vibration
            + rpm
            * self.profile.vibration_per_rpm
            * self.degradation.rpm_vibration_coupling_multiplier
            + self.random.gauss(
                0.0,
                self.profile.vibration_noise,
            )
        )

        vibration = (
            vibration
            * self.degradation.vibration_multiplier
            + self.degradation.vibration_offset
        )

        readings = [
            SensorReading(
                timestamp=timestamp,
                sensor="rpm",
                value=round(rpm, 3),
                unit="rpm",
            ),
            SensorReading(
                timestamp=timestamp,
                sensor="load",
                value=round(load, 3),
                unit="percent",
            ),
            SensorReading(
                timestamp=timestamp,
                sensor="temperature",
                value=round(
                    temperature,
                    3,
                ),
                unit="C",
            ),
            SensorReading(
                timestamp=timestamp,
                sensor="current",
                value=round(
                    current,
                    3,
                ),
                unit="A",
            ),
            SensorReading(
                timestamp=timestamp,
                sensor="vibration",
                value=round(
                    vibration,
                    3,
                ),
                unit="mm/s",
            ),
        ]

        return MachineSnapshot(
            machine_id=self.config.machine_id,
            timestamp=timestamp,
            readings=readings,
        )
