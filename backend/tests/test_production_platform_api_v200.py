from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_readiness_api():
    r=client.get("/api/v1/production-platform/readiness"); assert r.status_code==200 and r.json()["version"]=="2.0.0"
def test_quality_api():
    r=client.post("/api/v1/production-platform/data/quality",json={"record":{"x":1},"required":["x"]}); assert r.status_code==200 and r.json()["ok"]
