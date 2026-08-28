from __future__ import annotations

from dataclasses import dataclass

from app.mlops.champion import ChampionChallengerEngine, ModelEvaluation
from app.mlops.monitoring import ModelMonitoringEngine
from app.mlops.observability import MLOpsObservability
from app.mlops.registry import ModelRegistry
from app.mlops.retraining import RetrainingContext, RetrainingPolicyEngine


@dataclass(frozen=True)
class ControlPlaneAssessment:
    model_name: str
    champion_version: str | None
    monitoring_state: str
    retraining_required: bool
    retraining_urgency: str


class MLOpsControlPlane:
    def __init__(
        self,
        registry: ModelRegistry,
        monitoring: ModelMonitoringEngine | None = None,
        retraining: RetrainingPolicyEngine | None = None,
        observability: MLOpsObservability | None = None,
    ) -> None:
        self.registry = registry
        self.monitoring = monitoring or ModelMonitoringEngine()
        self.retraining = retraining or RetrainingPolicyEngine()
        self.observability = observability or MLOpsObservability()
        self.champion_engine = ChampionChallengerEngine()

    def assess(
        self,
        *,
        model_name: str,
        reference_predictions: list[float],
        current_predictions: list[float],
        reference_features: dict[str, list[float]] | None = None,
        current_features: dict[str, list[float]] | None = None,
        new_failure_samples: int = 0,
        days_since_training: int = 0,
    ) -> ControlPlaneAssessment:
        snapshot = self.monitoring.analyze(
            reference_predictions=reference_predictions,
            current_predictions=current_predictions,
            reference_features=reference_features,
            current_features=current_features,
        )

        retraining = self.retraining.decide(
            RetrainingContext(
                feature_drift_score=snapshot.feature_drift_score,
                prediction_drift_score=snapshot.prediction_drift_score,
                quality_score=snapshot.quality_score,
                new_failure_samples=new_failure_samples,
                days_since_training=days_since_training,
            )
        )

        champion = self.registry.champion(model_name)
        self.observability.increment("control_plane_assessments_total")
        if retraining.should_retrain:
            self.observability.increment("retraining_recommendations_total")

        return ControlPlaneAssessment(
            model_name=model_name,
            champion_version=champion.version if champion else None,
            monitoring_state=snapshot.state,
            retraining_required=retraining.should_retrain,
            retraining_urgency=retraining.urgency,
        )

    def compare_models(self, champion: ModelEvaluation, challenger: ModelEvaluation):
        decision = self.champion_engine.compare(champion, challenger)
        self.observability.increment("champion_challenger_evaluations_total")
        return decision
