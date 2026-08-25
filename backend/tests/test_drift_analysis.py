import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app


def create_machine(
    client: TestClient,
) -> str:
    response = client.post(
        "/api/v1/machines",
        json={
            "machine_code": f"DRIFT-{uuid.uuid4().hex[:10]}",
            "name": "Drift Test Machine",
            "machine_type": "cnc_milling",
            "status": "active",
            "metadata": {},
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def add_window(
    client: TestClient,
    machine_id: str,
    *,
    start_time: datetime,
    samples: int,
    vibration_offset: float = 0.0,
    temperature_offset: float = 0.0,
    current_offset: float = 0.0,
) -> None:
    measurements = []

    for index in range(samples):
        timestamp = (
            start_time
            + timedelta(seconds=index)
        ).isoformat()

        load = 60.0 + (index % 10) * 0.5
        rpm = 4100.0 + (index % 20) * 5.0

        current = (
            1.2
            + load * 0.105
            + current_offset
        )

        temperature = (
            42.0
            + load * 0.34
            + temperature_offset
        )

        vibration = (
            0.35
            + rpm * 0.00043
            + vibration_offset
        )

        rows = [
            ("load", load, "percent"),
            ("rpm", rpm, "rpm"),
            ("current", current, "A"),
            ("temperature", temperature, "C"),
            ("vibration", vibration, "mm/s"),
        ]

        for sensor, value, unit in rows:
            measurements.append(
                {
                    "machine_id": machine_id,
                    "timestamp": timestamp,
                    "sensor": sensor,
                    "value": value,
                    "unit": unit,
                }
            )

    response = client.post(
        "/api/v1/telemetry/batch",
        json={
            "measurements": measurements,
        },
    )

    assert response.status_code == 201


def test_slow_drift_analysis() -> None:
    with TestClient(app) as client:
        machine_id = create_machine(client)

        baseline_start = datetime.now(
            timezone.utc
        ).replace(microsecond=0)

        add_window(
            client,
            machine_id,
            start_time=baseline_start,
            samples=100,
        )

        baseline_response = client.post(
            f"/api/v1/machines/{machine_id}/dna/build"
        )

        assert baseline_response.status_code == 201

        baseline = baseline_response.json()

        start_time = (
            datetime.fromisoformat(
                baseline["window_end"].replace(
                    "Z",
                    "+00:00",
                )
            )
            + timedelta(seconds=1)
        )

        offsets = [
            (0.05, 0.5, 0.1),
            (0.15, 1.0, 0.2),
            (0.30, 2.0, 0.4),
            (0.60, 3.5, 0.7),
            (1.20, 5.0, 1.1),
            (2.00, 7.0, 1.6),
        ]

        for window_index, (
            vibration_offset,
            temperature_offset,
            current_offset,
        ) in enumerate(offsets):
            add_window(
                client,
                machine_id,
                start_time=(
                    start_time
                    + timedelta(
                        seconds=window_index * 100
                    )
                ),
                samples=50,
                vibration_offset=vibration_offset,
                temperature_offset=temperature_offset,
                current_offset=current_offset,
            )

        response = client.post(
            f"/api/v1/machines/{machine_id}/drift/analyze"
        )

        assert response.status_code == 200

        result = response.json()

        assert result["window_size"] == 50
        assert result["window_count"] == 6

        assert result["state"] == "drifting"
        assert result["overall_score"] >= 0.60

        assert (
            result["windows"][0]["deviation_score"]
            <
            result["windows"][-1]["deviation_score"]
        )

        assert (
            result["signals"][
                "vibration__mean_zscore"
            ]["state"]
            == "drifting"
        )

        assert (
            result["signals"][
                "temperature__mean_zscore"
            ]["state"]
            in {
                "emerging",
                "drifting",
            }
        )

        assert (
            result["signals"][
                "current__mean_zscore"
            ]["state"]
            in {
                "emerging",
                "drifting",
            }
        )


def test_drift_without_baseline() -> None:
    with TestClient(app) as client:
        machine_id = create_machine(client)

        response = client.post(
            f"/api/v1/machines/{machine_id}/drift/analyze"
        )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Machine DNA baseline not found"
    }


def test_drift_missing_machine() -> None:
    missing_id = uuid.uuid4()

    with TestClient(app) as client:
        response = client.post(
            f"/api/v1/machines/{missing_id}/drift/analyze"
        )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Machine not found"
    }
