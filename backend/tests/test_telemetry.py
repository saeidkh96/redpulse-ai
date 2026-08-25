import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app


def test_telemetry_ingestion_flow() -> None:
    machine_code = f"TEL-{uuid.uuid4().hex[:8]}"

    with TestClient(app) as client:
        machine_response = client.post(
            "/api/v1/machines",
            json={
                "machine_code": machine_code,
                "name": "Telemetry Test Machine",
                "machine_type": "test_machine",
                "status": "active",
                "metadata": {},
            },
        )

        assert machine_response.status_code == 201

        machine_id = machine_response.json()["id"]

        base_time = datetime.now(timezone.utc).replace(
            microsecond=0
        )

        single_payload = {
            "machine_id": machine_id,
            "timestamp": base_time.isoformat(),
            "sensor": "VIBRATION",
            "value": 2.41,
            "unit": "mm/s",
        }

        single_response = client.post(
            "/api/v1/telemetry",
            json=single_payload,
        )

        assert single_response.status_code == 201

        created = single_response.json()

        assert created["machine_id"] == machine_id
        assert created["sensor"] == "vibration"
        assert created["value"] == 2.41
        assert created["unit"] == "mm/s"

        duplicate_response = client.post(
            "/api/v1/telemetry",
            json=single_payload,
        )

        assert duplicate_response.status_code == 409
        assert duplicate_response.json() == {
            "detail": "Telemetry measurement already exists"
        }

        batch_time = base_time + timedelta(minutes=1)

        batch_payload = {
            "measurements": [
                {
                    "machine_id": machine_id,
                    "timestamp": batch_time.isoformat(),
                    "sensor": "temperature",
                    "value": 64.8,
                    "unit": "C",
                },
                {
                    "machine_id": machine_id,
                    "timestamp": batch_time.isoformat(),
                    "sensor": "current",
                    "value": 7.92,
                    "unit": "A",
                },
                {
                    "machine_id": machine_id,
                    "timestamp": batch_time.isoformat(),
                    "sensor": "vibration",
                    "value": 2.46,
                    "unit": "mm/s",
                },
            ]
        }

        batch_response = client.post(
            "/api/v1/telemetry/batch",
            json=batch_payload,
        )

        assert batch_response.status_code == 201
        assert batch_response.json() == {
            "inserted": 3
        }

        list_response = client.get(
            f"/api/v1/telemetry/machines/{machine_id}"
        )

        assert list_response.status_code == 200

        measurements = list_response.json()

        assert len(measurements) == 4
        assert measurements[0]["timestamp"] >= measurements[-1]["timestamp"]

        vibration_response = client.get(
            f"/api/v1/telemetry/machines/{machine_id}",
            params={"sensor": "vibration"},
        )

        assert vibration_response.status_code == 200

        vibration_measurements = vibration_response.json()

        assert len(vibration_measurements) == 2
        assert all(
            item["sensor"] == "vibration"
            for item in vibration_measurements
        )

        range_response = client.get(
            f"/api/v1/telemetry/machines/{machine_id}",
            params={
                "start": (
                    base_time + timedelta(seconds=30)
                ).isoformat(),
                "end": (
                    batch_time + timedelta(seconds=30)
                ).isoformat(),
            },
        )

        assert range_response.status_code == 200
        assert len(range_response.json()) == 3

        invalid_range_response = client.get(
            f"/api/v1/telemetry/machines/{machine_id}",
            params={
                "start": (
                    base_time + timedelta(hours=2)
                ).isoformat(),
                "end": base_time.isoformat(),
            },
        )

        assert invalid_range_response.status_code == 422
        assert invalid_range_response.json() == {
            "detail": "start must be before or equal to end"
        }

        missing_machine_response = client.post(
            "/api/v1/telemetry",
            json={
                "machine_id": str(uuid.uuid4()),
                "timestamp": base_time.isoformat(),
                "sensor": "temperature",
                "value": 70.0,
                "unit": "C",
            },
        )

        assert missing_machine_response.status_code == 404
        assert missing_machine_response.json() == {
            "detail": "Machine not found"
        }
