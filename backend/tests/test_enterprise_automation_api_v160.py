from fastapi.testclient import TestClient
from app.main import app

def test_v160_openapi_routes():
    paths = app.openapi()["paths"]
    assert "/api/v1/enterprise-automation/tenants" in paths
    assert "/api/v1/enterprise-automation/integrations" in paths
    assert "/api/v1/enterprise-automation/dispatch" in paths
