import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_machine_registry_flow() -> None:
    machine_code = f"TEST-{uuid.uuid4().hex[:8]}"

    create_payload = {
        "machine_code": machine_code,
        "name": "Test CNC Machine",
        "manufacturer": "Test Manufacturer",
        "model": "T-1000",
        "machine_type": "cnc_milling",
        "location": "Test Hall",
        "installation_date": "2025-01-10",
        "status": "active",
        "metadata": {
            "line": "Test-Line",
            "criticality": "high",
        },
    }

    with TestClient(app) as client:
        create_response = client.post(
            "/api/v1/machines",
            json=create_payload,
        )

        assert create_response.status_code == 201

        created = create_response.json()

        assert created["machine_code"] == machine_code
        assert created["name"] == "Test CNC Machine"
        assert created["status"] == "active"
        assert created["metadata"]["criticality"] == "high"

        machine_id = created["id"]

        get_response = client.get(
            f"/api/v1/machines/{machine_id}"
        )

        assert get_response.status_code == 200
        fetched = get_response.json()

        assert fetched["id"] == machine_id
        assert fetched["machine_code"] == machine_code

        list_response = client.get("/api/v1/machines")

        assert list_response.status_code == 200

        machines = list_response.json()

        assert any(
            machine["id"] == machine_id
            for machine in machines
        )

        patch_response = client.patch(
            f"/api/v1/machines/{machine_id}",
            json={
                "status": "maintenance",
                "location": "Maintenance Bay",
                "metadata": {
                    "criticality": "high",
                    "maintenance_reason": "automated test",
                },
            },
        )

        assert patch_response.status_code == 200

        updated = patch_response.json()

        assert updated["status"] == "maintenance"
        assert updated["location"] == "Maintenance Bay"
        assert (
            updated["metadata"]["maintenance_reason"]
            == "automated test"
        )
        assert updated["updated_at"] != created["updated_at"]

        duplicate_response = client.post(
            "/api/v1/machines",
            json=create_payload,
        )

        assert duplicate_response.status_code == 409
        assert duplicate_response.json() == {
            "detail": "Machine code already exists"
        }

        missing_id = uuid.uuid4()

        missing_response = client.get(
            f"/api/v1/machines/{missing_id}"
        )

        assert missing_response.status_code == 404
        assert missing_response.json() == {
            "detail": "Machine not found"
        }
