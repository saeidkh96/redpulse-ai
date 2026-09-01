from app.enterprise_integration_v38.core import IntegrationEndpoint, IntegrationRouter, Provider
from app.integrations_gateway.adapters import N8nAdapter, PowerAutomateAdapter, WebhookAdapter
from app.integrations_gateway.gateway import IntegrationEvent, IntegrationGateway
from app.mlops.champion import ChampionChallengerEngine, ModelEvaluation
from app.mlops.retraining import RetrainingContext, RetrainingPolicyEngine
from app.operational_validation_v40.core import OperationalEvidence, OperationalValidator
from app.orchestration_v36.pipelines import (
    maintenance_learning_pipeline,
    model_operations_pipeline,
    telemetry_intelligence_pipeline,
)
from app.orchestration_v36.service import ProductionOrchestrationService
from app.runtime_v3.idempotency import idempotency_key
from app.security_v3.policy import AuthorizationContext, TenantPolicy


def test_v36_orchestration_catalog():
    service = ProductionOrchestrationService()

    telemetry = service.build_plan(telemetry_intelligence_pipeline())
    maintenance = service.build_plan(maintenance_learning_pipeline())
    mlops = service.build_plan(model_operations_pipeline())

    assert telemetry.ordered_stages == (
        "telemetry_ingestion",
        "feature_processing",
        "machine_intelligence",
        "fleet_intelligence",
    )
    assert maintenance.ordered_stages == (
        "maintenance_history",
        "post_maintenance_verification",
        "outcome_learning",
    )
    assert mlops.ordered_stages == (
        "model_monitoring",
        "retraining_evaluation",
        "candidate_validation",
        "promotion_decision",
    )


def test_v36_retraining_policy():
    context = RetrainingContext(
        feature_drift_score=0.7,
        prediction_drift_score=0.6,
        quality_score=0.5,
        new_failure_samples=75,
        days_since_training=70,
    )

    decision = RetrainingPolicyEngine().decide(context)

    assert decision.should_retrain is True
    assert decision.urgency in {"medium", "high", "critical"}


def test_v36_champion_challenger():
    champion = ModelEvaluation(
        version="1",
        precision=0.82,
        recall=0.81,
        false_alert_rate=0.12,
        lead_time_score=0.75,
        maintenance_outcome_score=0.76,
    )

    challenger = ModelEvaluation(
        version="2",
        precision=0.90,
        recall=0.88,
        false_alert_rate=0.08,
        lead_time_score=0.84,
        maintenance_outcome_score=0.86,
    )

    decision = ChampionChallengerEngine().compare(champion, challenger)

    assert decision.challenger_won is True
    assert decision.winner_version == "2"


def test_v36_integration_gateway_catalog():
    gateway = IntegrationGateway()
    gateway.register("webhook", WebhookAdapter("http://localhost/webhook"))
    gateway.register("n8n", N8nAdapter("http://localhost/n8n"))
    gateway.register("power_automate", PowerAutomateAdapter("http://localhost/power-automate"))

    assert gateway.adapters() == ["n8n", "power_automate", "webhook"]


def test_v36_enterprise_integration_request_contract():
    router = IntegrationRouter()
    endpoint = IntegrationEndpoint(
        provider=Provider.N8N,
        url="http://localhost:5678/webhook/redpulse",
    )

    request = router.build_request(
        endpoint,
        "maintenance.alert",
        {"machine_id": "M-100"},
    )

    assert request.full_url == endpoint.url
    assert request.get_method() == "POST"
    assert request.headers["Content-type"] == "application/json"


def test_v36_security_policy():
    policy = TenantPolicy()
    context = AuthorizationContext(
        tenant_id="tenant-a",
        roles=frozenset({"engineer"}),
    )

    assert policy.allowed(context, "read") is True
    assert policy.allowed(context, "investigate") is True
    assert policy.allowed(context, "approve") is False


def test_v36_idempotency_is_deterministic():
    first = idempotency_key(
        "maintenance",
        {"machine_id": "M-100", "action": "inspect"},
    )
    second = idempotency_key(
        "maintenance",
        {"action": "inspect", "machine_id": "M-100"},
    )

    assert first == second


def test_v36_operational_validation_gate():
    evidence = OperationalEvidence(
        ci_passed=True,
        migrations_passed=True,
        docker_build_passed=True,
        security_scan_passed=True,
        load_test_passed=True,
        recovery_drill_passed=True,
        deployment_verified=True,
    )

    result = OperationalValidator().evaluate(evidence)

    assert result["ready"] is True
    assert result["production_validated"] is True
