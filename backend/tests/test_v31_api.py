from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_readiness(): assert client.get('/api/v1/v3.1/readiness').json()['healthy'] is True
def test_twin_and_predictive():
    assert client.post('/api/v1/v3.1/digital-twins',json={'machine_id':'m31','telemetry':{'load':.5,'vibration':.2},'health_score':.85,'deviation_score':.2,'drift_score':.1}).status_code==200
    assert client.post('/api/v1/v3.1/digital-twins/simulate',json={'machine_id':'m31','name':'stress','overrides':{'load':.95},'horizon_hours':72}).status_code==200
    assert client.post('/api/v1/v3.1/predictive/fusion',json={'modalities':{'telemetry':[.8,.9],'vision':[.5,.6]}}).status_code==200
    assert client.post('/api/v1/v3.1/predictive/rul',json={'health_score':.7,'drift_score':.2,'max_hours':1000}).status_code==200
