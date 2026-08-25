import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app


def create_machine(client: TestClient) -> str:
    code = f"DEV-{uuid.uuid4().hex[:10]}"

    response = client.post(
        "/api/v1/machines",
        json={
            "machine_code": code,
            "name": "Deviation Test Machine",
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


def test_behavioral_deviation_ladder() -> None:
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

        normal_start = (
            datetime.fromisoformat(
                baseline["window_end"].replace(
                    "Z",
                    "+00:00",
                )
            )
            + timedelta(seconds=1)
        )

        add_window(
            client,
            machine_id,
            start_time=normal_start,
            samples=100,
        )

        normal_response = client.post(
            f"/api/v1/machines/{machine_id}/deviation/analyze"
        )

        assert normal_response.status_code == 200

        normal = normal_response.json()

        assert normal["severity"] == "normal"
        assert normal["sample_count"] == 100

        moderate_start = (
            normal_start
            + timedelta(seconds=200)
        )

        add_window(
            client,
            machine_id,
            start_time=moderate_start,
            samples=100,
            vibration_offset=0.8,
            temperature_offset=4.0,
            current_offset=0.8,
        )

        moderate_response = client.post(
            f"/api/v1/machines/{machine_id}/deviation/analyze"
        )

        assert moderate_response.status_code == 200

        moderate = moderate_response.json()

        assert moderate["severity"] in {
            "warning",
            "anomalous",
        }

        severe_start = (
            moderate_start
            + timedelta(seconds=200)
        )

        add_window(
            client,
            machine_id,
            start_time=severe_start,
            samples=100,
            vibration_offset=4.0,
            temperature_offset=8.0,
            current_offset=2.0,
        )

        severe_response = client.post(
            f"/api/v1/machines/{machine_id}/deviation/analyze"
        )

        assert severe_response.status_code == 200

        severe = severe_response.json()

        assert severe["severity"] == "anomalous"
        assert severe["sample_count"] == 100

        assert (
            severe["sensor_deviations"]["vibration"][
                "mean_zscore"
            ]
            >= 5.0
        )


def test_deviation_without_baseline() -> None:
    with TestClient(app) as client:
        machine_id = create_machine(client)

        response = client.post(
            f"/api/v1/machines/{machine_id}/deviation/analyze"
        )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Machine DNA baseline not found"
    }


def test_deviation_missing_machine() -> None:
    missing_id = uuid.uuid4()

    with TestClient(app) as client:
        response = client.post(
            f"/api/v1/machines/{missing_id}/deviation/analyze"
        )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Machine not found"
    }
