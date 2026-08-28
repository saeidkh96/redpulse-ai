from __future__ import annotations


class MLflowAdapter:
    def __init__(self, tracking_uri: str | None = None) -> None:
        self.tracking_uri = tracking_uri

    def log_run(self, experiment_name: str, parameters: dict, metrics: dict) -> str:
        try:
            import mlflow
        except ImportError as exc:
            raise RuntimeError(
                "MLflow integration requires the optional MLOps dependencies."
            ) from exc

        if self.tracking_uri:
            mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(experiment_name)
        with mlflow.start_run() as run:
            mlflow.log_params(parameters)
            mlflow.log_metrics(metrics)
            return run.info.run_id
