from fastapi.testclient import TestClient

from app.main import app


def test_root() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "RedPulse AI"
    assert response.json()["version"] == "0.1.2"
    assert response.json()["status"] == "running"


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "redpulse-ai",
    }


def test_readiness() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/ready")

    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "ready"
    assert payload["service"] == "redpulse-ai"
    assert payload["dependencies"]["database"] == "up"
    assert payload["dependencies"]["redis"] == "up"
