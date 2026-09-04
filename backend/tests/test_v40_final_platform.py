from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.platform_v40.agents import AgenticMaintenanceOrchestrator, WorkflowState
from app.platform_v40.evaluation import Evaluator, PerformanceBenchmark
from app.platform_v40.governance import AuditEvent, AuditLog, FixedWindowRateLimiter, Identity, Policy, PolicyEngine
from app.platform_v40.hardening import DependencyProbe, Environment, IdempotencyRegistry, RuntimeProfile
from app.platform_v40.integrations import DeliveryRequest, EnterpriseIntegrationGateway, IntegrationAdapter, SignedWebhook
from app.platform_v40.intelligence import IntelligenceInput, PredictiveMaintenanceEngine
from app.platform_v40.mlops import DeploymentStage, DriftMonitor, ModelVersion, ProductionModelRegistry
from app.platform_v40.observability import PlatformMetrics
from app.platform_v40.release import V40Evidence, V40ReleaseGate
from app.platform_v40.streaming import ConsumerGroup, EventSchema, ReplayableEventLog, SchemaRegistry


def test_phase_a_hardening_contracts():
    RuntimeProfile(Environment.PRODUCTION, debug=False).validate()
    with pytest.raises(ValueError): RuntimeProfile(Environment.PRODUCTION, debug=True).validate()
    probe = DependencyProbe(); probe.register("db", lambda: True); probe.register("redis", lambda: True)
    assert probe.readiness()["ready"]
    idem = IdempotencyRegistry(); calls = {"n": 0}
    def op(): calls["n"] += 1; return calls["n"]
    assert idem.execute_once("k", op)["value"] == 1
    assert idem.execute_once("k", op)["duplicate"] and calls["n"] == 1


def test_phase_b_streaming_schema_replay_and_consumer_group():
    registry = SchemaRegistry(); registry.register(EventSchema("telemetry", 1, ("machine_id", "value")))
    log = ReplayableEventLog(registry)
    log.append("telemetry", "m1", {"machine_id": "m1", "value": 1}, "telemetry", 1, "e1")
    log.append("telemetry", "m1", {"machine_id": "m1", "value": 2}, "telemetry", 1, "e2")
    group = ConsumerGroup("intelligence")
    assert group.lag(log, "telemetry") == 2
    assert group.consume(log, "telemetry", lambda r: r.payload["value"]) == [1, 2]
    assert group.lag(log, "telemetry") == 0
    group.rewind("telemetry", 0)
    assert group.consume(log, "telemetry", lambda r: r.payload["value"]) == []


def test_phase_c_mlops_champion_challenger_drift_and_rollback():
    registry = ProductionModelRegistry()
    registry.register(ModelVersion("risk", "1", {"f1": .80}, "d1")); registry.promote("risk", "1")
    registry.register(ModelVersion("risk", "2", {"f1": .85}, "d2")); registry.set_challenger("risk", "2")
    assert registry.compare("risk", "2", "f1")["winner"] == "2"
    registry.promote("risk", "2"); assert registry.champion("risk").version == "2"
    registry.rollback("risk", "1"); assert registry.champion("risk").version == "1"
    assert DriftMonitor(.2).evaluate(.1, .25, .05).retraining_required


def test_phase_d_unified_intelligence_engine():
    decision = PredictiveMaintenanceEngine().evaluate(IntelligenceInput("m1", (0, 0), (1, 1), .9, .9, .05))
    assert decision.failure_risk > .5
    assert 0 <= decision.health_score <= 100
    assert decision.evidence


def test_phase_e_agentic_human_approval_gate():
    decision = PredictiveMaintenanceEngine().evaluate(IntelligenceInput("m1", (0, 0), (1, 1), .9, .9, .05))
    orchestrator = AgenticMaintenanceOrchestrator(); workflow = orchestrator.create(decision)
    assert workflow.state is WorkflowState.AWAITING_APPROVAL
    with pytest.raises(PermissionError): orchestrator.mark_dispatched(workflow)
    orchestrator.approve(workflow, "operator-1"); orchestrator.mark_dispatched(workflow); orchestrator.verify(workflow, True)
    assert workflow.state is WorkflowState.VERIFIED


def test_phase_f_enterprise_integrations_signing_retry_and_idempotency():
    payload = {"risk": .8}; signature = SignedWebhook.sign(payload, "secret")
    assert SignedWebhook.verify(payload, "secret", signature)
    calls = {"n": 0}
    def sender(req):
        calls["n"] += 1
        if calls["n"] == 1: raise TimeoutError("retry")
        return "accepted"
    gateway = EnterpriseIntegrationGateway(max_attempts=3); gateway.register(IntegrationAdapter.WEBHOOK, sender)
    request = DeliveryRequest(IntegrationAdapter.WEBHOOK, "t1", "failure-risk", "k1", payload)
    receipt = gateway.dispatch(request); assert receipt.delivered and receipt.attempts == 2
    assert gateway.dispatch(request) is receipt and calls["n"] == 2


def test_phase_g_security_governance_rate_limit_audit_and_metrics():
    identity = Identity("u1", "t1", frozenset({"operator"}))
    PolicyEngine().authorize(identity, "t1", Policy("maintenance.approve", frozenset({"operator", "admin"})))
    with pytest.raises(PermissionError): PolicyEngine().authorize(identity, "t2", Policy("x", frozenset({"operator"})))
    audit = AuditLog(); audit.record(AuditEvent("u1", "t1", "approve", "workflow:1", "success")); assert len(audit.for_tenant("t1")) == 1
    limiter = FixedWindowRateLimiter(2, 60); now = datetime.now(timezone.utc)
    assert limiter.allow("u", now) and limiter.allow("u", now) and not limiter.allow("u", now)
    assert limiter.allow("u", now + timedelta(seconds=61))
    metrics = PlatformMetrics()
    for name in metrics.REQUIRED_GAUGES: metrics.set_gauge(name, 1)
    for name in metrics.REQUIRED_COUNTERS: metrics.increment(name)
    assert metrics.coverage()["complete"]


def test_phase_h_evaluation_and_benchmarking():
    result = Evaluator.classification([1, 1, 0, 0], [1, 0, 1, 0])
    assert result.precision == .5 and result.recall == .5 and result.f1 == .5
    assert Evaluator.early_warning_lead_time([10, 20], [7, 15]) == 4
    benchmark = PerformanceBenchmark().run(20, lambda i: i * i)
    assert benchmark.operations == 20 and benchmark.throughput_ops_s > 0


def test_phase_i_release_gate_and_api():
    from app.main import app
    evidence = V40Evidence(**{field: True for field in V40Evidence.__dataclass_fields__})
    assert V40ReleaseGate().evaluate(evidence)["ready"]
    with TestClient(app) as client:
        root = client.get("/"); assert root.status_code == 200 and root.json()["version"] == "4.0.0"
        caps = client.get("/api/v1/platform/v40/capabilities"); assert caps.status_code == 200 and len(caps.json()["phases"]) == 9
        decision = client.post("/api/v1/platform/v40/intelligence/evaluate", json={"machine_id":"m1","baseline":[0,0],"current":[1,1],"drift_score":.9,"trajectory_match":.9})
        assert decision.status_code == 200 and decision.json()["failure_risk"] > .5
        gate = client.post("/api/v1/platform/v40/release-gate", json={field: True for field in V40Evidence.__dataclass_fields__})
        assert gate.status_code == 200 and gate.json()["ready"]
