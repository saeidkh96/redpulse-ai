from .contracts import OrchestrationPipeline, OrchestrationStage, RetryPolicy

DEFAULT_RETRY = RetryPolicy(max_attempts=3, retry_delay_seconds=60, exponential_backoff=True)


def telemetry_intelligence_pipeline() -> OrchestrationPipeline:
    return OrchestrationPipeline(
        name="redpulse_telemetry_intelligence",
        schedule="*/15 * * * *",
        stages=(
            OrchestrationStage("telemetry_ingestion", retry_policy=DEFAULT_RETRY),
            OrchestrationStage("feature_processing", depends_on=("telemetry_ingestion",), retry_policy=DEFAULT_RETRY),
            OrchestrationStage("machine_intelligence", depends_on=("feature_processing",), retry_policy=DEFAULT_RETRY),
            OrchestrationStage("fleet_intelligence", depends_on=("machine_intelligence",), retry_policy=DEFAULT_RETRY),
        ),
        metadata={"release": "v3.6.0", "domain": "telemetry"},
    )


def maintenance_learning_pipeline() -> OrchestrationPipeline:
    return OrchestrationPipeline(
        name="redpulse_maintenance_learning",
        schedule="0 * * * *",
        stages=(
            OrchestrationStage("maintenance_history", retry_policy=DEFAULT_RETRY),
            OrchestrationStage("post_maintenance_verification", depends_on=("maintenance_history",), retry_policy=DEFAULT_RETRY),
            OrchestrationStage("outcome_learning", depends_on=("post_maintenance_verification",), retry_policy=DEFAULT_RETRY),
        ),
        metadata={"release": "v3.6.0", "domain": "maintenance"},
    )


def model_operations_pipeline() -> OrchestrationPipeline:
    return OrchestrationPipeline(
        name="redpulse_model_operations",
        schedule="0 2 * * *",
        stages=(
            OrchestrationStage("model_monitoring", retry_policy=DEFAULT_RETRY),
            OrchestrationStage("retraining_evaluation", depends_on=("model_monitoring",), retry_policy=DEFAULT_RETRY),
            OrchestrationStage("candidate_validation", depends_on=("retraining_evaluation",), retry_policy=DEFAULT_RETRY),
            OrchestrationStage("promotion_decision", depends_on=("candidate_validation",), retry_policy=DEFAULT_RETRY),
        ),
        metadata={"release": "v3.6.0", "domain": "mlops"},
    )
