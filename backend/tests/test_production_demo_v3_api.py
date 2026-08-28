from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_v3_readiness():
    r = client.get("/api/v1/v3/readiness")
    assert r.status_code == 200
    assert r.json()["ready"] is True

def test_v3_demo_run():
    r = client.post("/api/v1/v3/demo/run", json={
        "tenant_id":"t1",
        "machine_id":"m1",
        "signals":{"health_score":0.2,"deviation_score":0.9,"drift_score":0.8}
    })
    assert r.status_code == 200
    assert r.json()["machine_id"] == "m1"
