import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app


def create_test_machine(client: TestClient) -> str:
    machine_code = f"DNA-{uuid.uuid4().hex[:10]}"

    response = client.post(
        "/api/v1/machines",
        json={
            "machine_code": machine_code,
            "name": "Machine DNA Test",
            "machine_type": "cnc_milling",
            "status": "active",
            "metadata": {
                "purpose": "machine-dna-test",
            },
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_test_telemetry(
    client: TestClient,
    machine_id: str,
    sample_count: int = 20,
) -> None:
    base_time = datetime.now(
        timezone.utc
    ).replace(
        microsecond=0
    )

    measurements = []

    for index in range(sample_count):
        timestamp = (
            base_time
            + timedelta(seconds=index)
        ).isoformat()

        load = 50.0 + index
        rpm = 4000.0 + index * 10.0

        measurements.extend(
            [
                {
                    "machine_id": machine_id,
                    "timestamp": timestamp,
                    "sensor": "load",
                    "value": load,
                    "unit": "percent",
                },
                {
                    "machine_id": machine_id,
                    "timestamp": timestamp,
                    "sensor": "current",
                    "value": 1.0 + load * 0.1,
                    "unit": "A",
                },
                {
                    "machine_id": machine_id,
                    "timestamp": timestamp,
                    "sensor": "temperature",
                    "value": 40.0 + load * 0.3,
                    "unit": "C",
                },
                {
                    "machine_id": machine_id,
                    "timestamp": timestamp,
                    "sensor": "rpm",
                    "value": rpm,
                    "unit": "rpm",
                },
                {
                    "machine_id": machine_id,
                    "timestamp": timestamp,
                    "sensor": "vibration",
                    "value": 0.3 + rpm * 0.0004,
                    "unit": "mm/s",
                },
            ]
        )

    response = client.post(
        "/api/v1/telemetry/batch",
        json={
            "measurements": measurements,
        },
    )

    assert response.status_code == 201
    assert response.json()["inserted"] == (
        sample_count * 5
    )


def test_build_machine_dna() -> None:
    with TestClient(app) as client:
        machine_id = create_test_machine(client)

        create_test_telemetry(
            client,
            machine_id,
            sample_count=20,
        )

        response = client.post(
            f"/api/v1/machines/{machine_id}/dna/build"
        )

        assert response.status_code == 201

        baseline = response.json()

        assert baseline["machine_id"] == machine_id
        assert baseline["baseline_version"] == "1"
        assert baseline["sample_count"] == 20

        assert set(
            baseline["sensor_features"].keys()
        ) == {
            "load",
            "current",
            "temperature",
            "rpm",
            "vibration",
        }

        assert (
            baseline["correlations"][
                "current__load"
            ]
            > 0.99
        )

        assert (
            baseline["correlations"][
                "load__temperature"
            ]
            > 0.99
        )

        assert (
            baseline["correlations"][
                "rpm__vibration"
            ]
            > 0.99
        )


def test_machine_dna_versioning() -> None:
    with TestClient(app) as client:
        machine_id = create_test_machine(client)

        create_test_telemetry(
            client,
            machine_id,
            sample_count=10,
        )

        version_1_response = client.post(
            f"/api/v1/machines/{machine_id}/dna/build"
        )

        assert version_1_response.status_code == 201
        version_1 = version_1_response.json()

        assert version_1["baseline_version"] == "1"

        version_2_response = client.post(
            f"/api/v1/machines/{machine_id}/dna/build"
        )

        assert version_2_response.status_code == 201
        version_2 = version_2_response.json()

        assert version_2["baseline_version"] == "2"
        assert version_2["id"] != version_1["id"]

        version_3_response = client.post(
            f"/api/v1/machines/{machine_id}/dna/build"
        )

        assert version_3_response.status_code == 201
        version_3 = version_3_response.json()

        assert version_3["baseline_version"] == "3"

        latest_response = client.get(
            f"/api/v1/machines/{machine_id}/dna"
        )

        assert latest_response.status_code == 200

        latest = latest_response.json()

        assert latest["id"] == version_3["id"]
        assert latest["baseline_version"] == "3"


def test_machine_dna_without_telemetry() -> None:
    with TestClient(app) as client:
        machine_id = create_test_machine(client)

        response = client.post(
            f"/api/v1/machines/{machine_id}/dna/build"
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "No telemetry available for machine"
        }


def test_machine_dna_missing_machine() -> None:
    missing_id = uuid.uuid4()

    with TestClient(app) as client:
        response = client.post(
            f"/api/v1/machines/{missing_id}/dna/build"
        )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Machine not found"
    }


def test_get_missing_machine_dna() -> None:
    with TestClient(app) as client:
        machine_id = create_test_machine(client)

        response = client.get(
            f"/api/v1/machines/{machine_id}/dna"
        )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Machine DNA not found"
    }
