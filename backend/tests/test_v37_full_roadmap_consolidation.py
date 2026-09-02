from app.advanced_predictive_v31.core import ProbabilisticRUL, UncertaintyEstimator
from app.mlops.champion import ChampionChallengerEngine, ModelEvaluation
from app.mlops.retraining import RetrainingContext, RetrainingPolicyEngine
from app.operational_validation_v40.core import OperationalEvidence
from app.orchestration_v36.pipelines import telemetry_intelligence_pipeline
from app.orchestration_v36.service import ProductionOrchestrationService
from app.platform_expansion_v37 import (
    AICostLedger,
    AIUsageRecord,
    AutonomousMaintenanceCoordinator,
    BenchmarkObservation,
    ConsolidatedReleaseManifest,
    CostBudget,
    DecisionTrace,
    ExecutionState,
    ExecutionToken,
    FleetKnowledgeTransferGate,
    MaintenanceExecutionIntent,
    MaintenanceIntentState,
    OperationalEvidenceLedger,
    PerformanceBenchmarkEvaluator,
    PerformanceSLO,
    PlatformConvergenceGate,
    ResilientStageRunner,
    TenantIsolationGuard,
    TransferCandidate,
)
from app.security_v3.policy import AuthorizationContext


def test_release_manifest_consolidates_roadmap_under_v370():
    manifest = ConsolidatedReleaseManifest()
    assert manifest.tag == "v3.7.0"
    assert len(manifest.consolidated_roadmap) == 10
    assert "AI FinOps & Cost Intelligence" in manifest.consolidated_roadmap
    assert "Autonomous Industrial Intelligence Platform" in manifest.consolidated_roadmap


def test_existing_orchestration_is_reused():
    plan = ProductionOrchestrationService().build_plan(telemetry_intelligence_pipeline())
    assert plan.ordered_stages == (
        "telemetry_ingestion",
        "feature_processing",
        "machine_intelligence",
        "fleet_intelligence",
    )


def test_resilient_runner_retries_then_replays_without_duplicate_work():
    runner = ResilientStageRunner()
    calls = {"count": 0}

    def flaky_operation():
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("temporary failure")
        return {"prediction_id": "pred-1"}

    token = ExecutionToken("tenant-a", "wf-1", "predict", {"machine_id": "m-1"})
    first = runner.run(token, flaky_operation, max_attempts=2)
    second = runner.run(token, flaky_operation, max_attempts=2)

    assert first.state == ExecutionState.SUCCEEDED
    assert first.attempts == 2
    assert second.replayed is True
    assert calls["count"] == 2


def test_failed_stage_can_be_retried_after_failure_record_is_cleared():
    runner = ResilientStageRunner()
    token = ExecutionToken("tenant-a", "wf-2", "feature", {"event": "e-1"})
    failed = runner.run(token, lambda: (_ for _ in ()).throw(RuntimeError("down")), max_attempts=1)
    assert failed.state == ExecutionState.FAILED
    runner.ledger.clear_failed(token.key)
    recovered = runner.run(token, lambda: "ok", max_attempts=1)
    assert recovered.state == ExecutionState.SUCCEEDED


def test_tenant_isolation_guard_rejects_cross_tenant_execution():
    token = ExecutionToken("tenant-a", "wf", "stage", {})
    TenantIsolationGuard.validate(token, "tenant-a")
    try:
        TenantIsolationGuard.validate(token, "tenant-b")
    except PermissionError:
        pass
    else:
        raise AssertionError("cross-tenant execution was not rejected")


def test_operational_lineage_tracks_decision_chain_per_tenant():
    ledger = OperationalEvidenceLedger()
    trace = DecisionTrace(
        tenant_id="tenant-a",
        machine_id="machine-7",
        telemetry_source="kafka:telemetry",
        dataset_version="silver-12",
        feature_version="features-5",
        model_version="failure-risk-3",
        prediction_id="prediction-99",
        maintenance_decision_id="decision-44",
        outcome_id="outcome-2",
    )
    ledger.record(trace)
    assert ledger.complete(trace) is True
    assert ledger.for_tenant("tenant-a") == [trace]
    assert len(ledger.lineage.entries) == 1


def test_performance_benchmark_gate_evaluates_throughput_latency_and_errors():
    observations = [BenchmarkObservation(latency_ms=100 + i, succeeded=True) for i in range(100)]
    report = PerformanceBenchmarkEvaluator().evaluate(
        observations,
        duration_seconds=2.0,
        slo=PerformanceSLO(min_throughput_per_second=40, max_p95_latency_ms=200),
    )
    assert report.ready is True
    assert report.throughput_per_second == 50.0


def test_ai_finops_is_tenant_scoped_and_budget_aware():
    ledger = AICostLedger()
    ledger.record(AIUsageRecord("tenant-a", "copilot", "hf", 1000, 2.5))
    ledger.record(AIUsageRecord("tenant-a", "prediction", "local", 500, 1.0))
    ledger.record(AIUsageRecord("tenant-b", "copilot", "hf", 1000, 9.0))
    budget = ledger.evaluate_budget(CostBudget("tenant-a", limit_usd=10.0))
    assert ledger.tenant_cost("tenant-a") == 3.5
    assert budget["state"] == "healthy"
    assert budget["within_budget"] is True


def test_autonomous_maintenance_keeps_human_approval_boundary():
    coordinator = AutonomousMaintenanceCoordinator()
    intent = MaintenanceExecutionIntent("tenant-a", "m-1", "inspect_bearing", 0.92, 0.81)
    engineer = AuthorizationContext("tenant-a", frozenset({"engineer"}))
    approver = AuthorizationContext("tenant-a", frozenset({"approver"}))
    proposed = coordinator.evaluate(intent, engineer)
    approved = coordinator.evaluate(intent, approver)
    assert proposed["state"] == MaintenanceIntentState.PROPOSED
    assert approved["state"] == MaintenanceIntentState.APPROVED


def test_fleet_knowledge_transfer_requires_similarity_evidence_and_support():
    gate = FleetKnowledgeTransferGate()
    accepted = gate.evaluate(TransferCandidate("m-1", "m-2", 0.91, 0.82, 12))
    rejected = gate.evaluate(TransferCandidate("m-1", "m-3", 0.40, 0.90, 12))
    assert accepted.accepted is True
    assert rejected.accepted is False


def test_existing_advanced_predictive_foundations_are_reused():
    interval = UncertaintyEstimator().interval(0.7, 0.1)
    rul = ProbabilisticRUL().estimate(0.8, 0.2)
    assert interval.lower == 0.6
    assert interval.upper == 0.8
    assert rul["mean_hours"] > 0


def test_existing_mlops_foundations_are_reused():
    retraining = RetrainingPolicyEngine().decide(
        RetrainingContext(0.8, 0.7, 0.5, 80, 70)
    )
    champion = ModelEvaluation("1", 0.80, 0.80, 0.10, 0.70, 0.70)
    challenger = ModelEvaluation("2", 0.90, 0.90, 0.05, 0.80, 0.80)
    decision = ChampionChallengerEngine().compare(champion, challenger)
    assert retraining.should_retrain is True
    assert decision.challenger_won is True


def test_platform_convergence_gate_requires_all_evidence_dimensions():
    observations = [BenchmarkObservation(latency_ms=50.0) for _ in range(20)]
    benchmark = PerformanceBenchmarkEvaluator().evaluate(
        observations,
        duration_seconds=1.0,
        slo=PerformanceSLO(min_throughput_per_second=10, max_p95_latency_ms=100),
    )
    result = PlatformConvergenceGate().evaluate(
        operational_evidence=OperationalEvidence(
            ci_passed=True,
            migrations_passed=True,
            docker_build_passed=True,
            security_scan_passed=True,
            load_test_passed=True,
            recovery_drill_passed=True,
            deployment_verified=True,
        ),
        benchmark=benchmark,
        recovery_validated=True,
        replay_safe=True,
        lineage_complete=True,
        tenant_isolation_validated=True,
        cost_guardrails_validated=True,
    )
    assert result["ready"] is True
