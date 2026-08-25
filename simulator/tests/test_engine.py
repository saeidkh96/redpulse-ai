from datetime import datetime, timezone

from simulator.config import SimulatorConfig
from simulator.engine import CNCSimulator


def test_generate_snapshot() -> None:
    config = SimulatorConfig(
        machine_id="test-machine",
        seed=42,
    )

    simulator = CNCSimulator(config)

    timestamp = datetime(
        2026,
        8,
        25,
        20,
        0,
        tzinfo=timezone.utc,
    )

    snapshot = simulator.generate_snapshot(timestamp)

    assert snapshot.machine_id == "test-machine"
    assert snapshot.timestamp == timestamp
    assert len(snapshot.readings) == 5

    sensors = {
        reading.sensor
        for reading in snapshot.readings
    }

    assert sensors == {
        "rpm",
        "load",
        "temperature",
        "current",
        "vibration",
    }


def test_seed_is_reproducible() -> None:
    config_a = SimulatorConfig(
        machine_id="machine-a",
        seed=123,
    )

    config_b = SimulatorConfig(
        machine_id="machine-a",
        seed=123,
    )

    simulator_a = CNCSimulator(config_a)
    simulator_b = CNCSimulator(config_b)

    snapshot_a = simulator_a.generate_snapshot()
    snapshot_b = simulator_b.generate_snapshot()

    values_a = [
        reading.value
        for reading in snapshot_a.readings
    ]

    values_b = [
        reading.value
        for reading in snapshot_b.readings
    ]

    assert values_a == values_b


def test_generated_values_are_reasonable() -> None:
    config = SimulatorConfig(
        machine_id="machine-a",
        seed=42,
    )

    simulator = CNCSimulator(config)

    snapshot = simulator.generate_snapshot()

    values = {
        reading.sensor: reading.value
        for reading in snapshot.readings
    }

    assert 0 <= values["load"] <= 100
    assert values["rpm"] >= 0
    assert 40 <= values["temperature"] <= 90
    assert 0 <= values["current"] <= 20
    assert 0 <= values["vibration"] <= 10


def test_behavioral_correlations() -> None:
    config = SimulatorConfig(
        machine_id="machine-a",
        seed=999,
    )

    simulator = CNCSimulator(config)

    samples = []

    for _ in range(500):
        snapshot = simulator.generate_snapshot()

        values = {
            reading.sensor: reading.value
            for reading in snapshot.readings
        }

        samples.append(values)

    loads = [item["load"] for item in samples]
    temperatures = [item["temperature"] for item in samples]
    currents = [item["current"] for item in samples]

    rpms = [item["rpm"] for item in samples]
    vibrations = [item["vibration"] for item in samples]

    def correlation(x: list[float], y: list[float]) -> float:
        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)

        numerator = sum(
            (a - mean_x) * (b - mean_y)
            for a, b in zip(x, y)
        )

        denominator_x = sum(
            (a - mean_x) ** 2
            for a in x
        ) ** 0.5

        denominator_y = sum(
            (b - mean_y) ** 2
            for b in y
        ) ** 0.5

        return numerator / (
            denominator_x * denominator_y
        )

    load_temperature = correlation(
        loads,
        temperatures,
    )

    load_current = correlation(
        loads,
        currents,
    )

    rpm_vibration = correlation(
        rpms,
        vibrations,
    )

    assert load_temperature > 0.5
    assert load_current > 0.7
    assert rpm_vibration > 0.2

def test_baseline_sensor_correlations() -> None:
    config = SimulatorConfig(
        machine_id="baseline-machine",
        seed=2026,
    )

    simulator = CNCSimulator(config)

    snapshots = [
        simulator.generate_snapshot()
        for _ in range(1000)
    ]

    loads = []
    temperatures = []
    currents = []
    rpms = []
    vibrations = []

    for snapshot in snapshots:
        values = {
            reading.sensor: reading.value
            for reading in snapshot.readings
        }

        loads.append(values["load"])
        temperatures.append(values["temperature"])
        currents.append(values["current"])
        rpms.append(values["rpm"])
        vibrations.append(values["vibration"])

    def correlation(x: list[float], y: list[float]) -> float:
        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)

        numerator = sum(
            (a - mean_x) * (b - mean_y)
            for a, b in zip(x, y)
        )

        denominator_x = sum(
            (a - mean_x) ** 2
            for a in x
        ) ** 0.5

        denominator_y = sum(
            (b - mean_y) ** 2
            for b in y
        ) ** 0.5

        return numerator / (
            denominator_x * denominator_y
        )

    assert correlation(loads, temperatures) > 0.75
    assert correlation(loads, currents) > 0.80
    assert correlation(rpms, vibrations) > 0.25
