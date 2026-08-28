from app.production.control_plane import ProductionControlPlane
from app.production.automation_runtime import JobStatus
from app.production.predictive_ai import ModelRef, FailureRiskModel, DriftSignal, RetrainingPolicy, ChampionChallenger, FeatureContract, RemainingUsefulLifeModel
from app.production.data_platform import DataQuality, partition_fleet
from app.production.observability import RateLimiter, CircuitBreaker

def test_readiness():
    r=ProductionControlPlane().readiness(); assert r.ready and r.version=="2.0.0"
def test_approval_and_jobs():
    p=ProductionControlPlane(); a=p.approvals.request("t1","maintenance"); assert p.approvals.decide(a.approval_id,True,"operator").approved
    j=p.automation.submit("t1","n8n","risk",{}); p.automation.run(j.job_id,lambda _:None); assert j.status==JobStatus.SUCCEEDED
def test_predictive_runtime():
    p=ProductionControlPlane(); ref=ModelRef("failure","1"); p.models.register(ref,FailureRiskModel()); p.models.promote(ref); assert p.models.predict("failure",{"x":.8})["failure_risk"]==.8
    assert RetrainingPolicy().should_retrain(DriftSignal("failure",.4,.3)); assert ChampionChallenger.choose(.8,.9)=="challenger"
    FeatureContract("1",frozenset({"x"})).validate({"x":1}); assert RemainingUsefulLifeModel(100).predict({"d":.2})["rul_hours"]==80
def test_data_and_reliability():
    assert DataQuality.check({"x":1},{"x"})["ok"]; assert len(partition_fleet(["m1","m2"],2))==2
    cb=CircuitBreaker(2); cb.failure(); cb.failure(); assert not cb.allow(); assert RateLimiter(1).allow("x")
