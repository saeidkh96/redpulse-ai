from app.ml_runtime_v3.serving import ProductionModelRouter, ModelKey
from app.ml_runtime_v3.models import FailureRiskModel, RemainingUsefulLifeModel
from app.ml_runtime_v3.drift import DriftAssessment, RetrainingCoordinator

def test_model_router():
    router = ProductionModelRouter()
    key = ModelKey("failure-risk", "1")
    router.register(key, FailureRiskModel())
    router.activate(key)
    out = router.predict("failure-risk", {"health_score":0.5,"deviation_score":0.6,"drift_score":0.4})
    assert "failure_risk" in out["prediction"]

def test_rul_model():
    out = RemainingUsefulLifeModel(1000).predict({"health_score":0.8,"drift_score":0.2})
    assert 0 < out["remaining_useful_life_hours"] <= 1000

def test_retraining_trigger():
    coord = RetrainingCoordinator()
    result = coord.evaluate(DriftAssessment("m", 0.8, 0.5))
    assert result["triggered"]
    assert coord.requests
