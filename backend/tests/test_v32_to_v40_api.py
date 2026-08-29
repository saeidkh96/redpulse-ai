from fastapi.testclient import TestClient
from app.main import app
def test_routes():
 p=app.openapi()['paths']; expected=['/api/v1/v32-platform/lakehouse/process','/api/v1/v32-platform/governance/grants','/api/v1/v32-platform/hardening/readiness','/api/v1/v32-platform/operational-validation']; assert all(x in p for x in expected)
def test_lakehouse_api():
 with TestClient(app) as c: r=c.post('/api/v1/v32-platform/lakehouse/process',json={'machine_id':'M1','ts':'2026-08-29T00:00:00Z','metrics':{'temperature':65.0,'vibration':2.0}})
 assert r.status_code==200 and r.json()['gold']['layer']=='gold'
