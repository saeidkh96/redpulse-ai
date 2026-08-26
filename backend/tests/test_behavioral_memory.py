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
            "machine_code": f"MEM-{uuid.uuid4().hex[:10]}",
            "name": "Behavioral Memory Test Machine",
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


def test_behavioral_memory_flow() -> None:
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

        analysis_start = (
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
                    analysis_start
                    + timedelta(
                        seconds=window_index * 100
                    )
                ),
                samples=50,
                vibration_offset=vibration_offset,
                temperature_offset=temperature_offset,
                current_offset=current_offset,
            )

        deviation_response = client.post(
            f"/api/v1/machines/{machine_id}/deviation/analyze"
        )

        assert deviation_response.status_code == 200

        drift_response = client.post(
            f"/api/v1/machines/{machine_id}/drift/analyze"
        )

        assert drift_response.status_code == 200

        memory_response = client.get(
            f"/api/v1/machines/{machine_id}/memory"
        )

        assert memory_response.status_code == 200

        events = memory_response.json()

        assert len(events) == 2

        event_types = {
            event["event_type"]
            for event in events
        }

        assert event_types == {
            "deviation",
            "drift",
        }

        assert all(
            event["machine_id"] == machine_id
            for event in events
        )

        assert all(
            event["baseline_version"] == "1"
            for event in events
        )

        assert all(
            event["evidence"]
            for event in events
        )

        deviation_event = next(
            event
            for event in events
            if event["event_type"] == "deviation"
        )

        drift_event = next(
            event
            for event in events
            if event["event_type"] == "drift"
        )

        assert (
            deviation_event["severity"]
            in {
                "warning",
                "anomalous",
            }
        )

        assert (
            drift_event["severity"]
            == "anomalous"
        )

        assert (
            drift_event["evidence"]["state"]
            == "drifting"
        )

        event_id = deviation_event["id"]

        single_response = client.get(
            f"/api/v1/machines/{machine_id}/memory/{event_id}"
        )

        assert single_response.status_code == 200

        single_event = single_response.json()

        assert single_event["id"] == event_id
        assert single_event["machine_id"] == machine_id

        client.post(
            f"/api/v1/machines/{machine_id}/deviation/analyze"
        )

        client.post(
            f"/api/v1/machines/{machine_id}/drift/analyze"
        )

        repeated_memory_response = client.get(
            f"/api/v1/machines/{machine_id}/memory"
        )

        assert repeated_memory_response.status_code == 200

        repeated_events = repeated_memory_response.json()

        assert len(repeated_events) == 2


def test_behavioral_memory_filters() -> None:
    with TestClient(app) as client:
        machine_id = create_machine(client)

        response = client.get(
            f"/api/v1/machines/{machine_id}/memory"
            "?event_type=drift"
        )

        assert response.status_code == 200
        assert response.json() == []


def test_behavioral_memory_missing_machine() -> None:
    missing_id = uuid.uuid4()

    with TestClient(app) as client:
        response = client.get(
            f"/api/v1/machines/{missing_id}/memory"
        )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Machine not found"
    }


def test_behavioral_memory_missing_event() -> None:
    with TestClient(app) as client:
        machine_id = create_machine(client)
        missing_event_id = uuid.uuid4()

        response = client.get(
            f"/api/v1/machines/{machine_id}/memory/{missing_event_id}"
        )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Behavior event not found"
    }
