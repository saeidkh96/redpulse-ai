from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "RedPulse AI"
    assert response.json()["version"] == "0.0.1"
    assert response.json()["status"] == "running"


def test_health() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "redpulse-ai",
    }


def test_readiness() -> None:
    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "redpulse-ai",
    }
