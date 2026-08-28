from __future__ import annotations

from pathlib import Path

from app.mlops.control_plane import MLOpsControlPlane
from app.mlops.experiments import ExperimentRun, ExperimentTracker
from app.mlops.feature_store import FeatureStore
from app.mlops.lifecycle import ModelLifecycleManager
from app.mlops.registry import ModelRegistry, ModelVersion
from app.mlops.serving import ModelServingRouter


class MLOpsPlatformService:
    def __init__(self, base_path: str | Path = "artifacts/mlops") -> None:
        base = Path(base_path)
        self.registry = ModelRegistry(base / "model_registry.json")
        self.experiments = ExperimentTracker(base / "experiments.json")
        self.feature_store = FeatureStore(base / "feature_store.json")
        self.serving = ModelServingRouter()
        self.control_plane = MLOpsControlPlane(self.registry)
        self.lifecycle = ModelLifecycleManager(self.registry)

    def register_model(
        self,
        *,
        model_name: str,
        version: str,
        artifact_uri: str,
        framework: str,
        metrics: dict[str, float] | None = None,
        parameters: dict | None = None,
    ) -> ModelVersion:
        return self.registry.register(
            ModelVersion(
                model_name=model_name,
                version=version,
                artifact_uri=artifact_uri,
                framework=framework,
                metrics=metrics or {},
                parameters=parameters or {},
            )
        )

    def log_experiment(
        self,
        experiment_name: str,
        *,
        parameters: dict | None = None,
        metrics: dict[str, float] | None = None,
        tags: dict[str, str] | None = None,
    ) -> ExperimentRun:
        return self.experiments.log_run(
            ExperimentRun(
                experiment_name=experiment_name,
                parameters=parameters or {},
                metrics=metrics or {},
                tags=tags or {},
            )
        )
