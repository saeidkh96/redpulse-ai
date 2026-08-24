from fastapi.testclient import TestClient

from app.main import app


def test_infrastructure_readiness() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/ready")

    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "ready"
    assert payload["dependencies"]["database"] == "up"
    assert payload["dependencies"]["redis"] == "up"
