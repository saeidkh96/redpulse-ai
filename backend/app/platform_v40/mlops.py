from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class DeploymentStage(str, Enum):
    CANDIDATE = "candidate"
    CHALLENGER = "challenger"
    CHAMPION = "champion"
    ARCHIVED = "archived"
    ROLLED_BACK = "rolled_back"


@dataclass
class ModelVersion:
    model_name: str
    version: str
    metrics: dict[str, float]
    dataset_version: str
    stage: DeploymentStage = DeploymentStage.CANDIDATE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class DriftReport:
    data_drift: float
    prediction_drift: float
    performance_drop: float
    retraining_required: bool


class ProductionModelRegistry:
    def __init__(self) -> None:
        self.records: dict[tuple[str, str], ModelVersion] = {}
        self.deployment_history: list[dict[str, str]] = []

    def register(self, record: ModelVersion) -> ModelVersion:
        key = (record.model_name, record.version)
        if key in self.records:
            raise ValueError("model version already exists")
        self.records[key] = record
        return record

    def promote(self, model_name: str, version: str) -> ModelVersion:
        target = self.records[(model_name, version)]
        for record in self.records.values():
            if record.model_name == model_name and record.stage is DeploymentStage.CHAMPION:
                record.stage = DeploymentStage.ARCHIVED
        target.stage = DeploymentStage.CHAMPION
        self.deployment_history.append({"action": "promote", "model": model_name, "version": version})
        return target

    def set_challenger(self, model_name: str, version: str) -> ModelVersion:
        target = self.records[(model_name, version)]
        target.stage = DeploymentStage.CHALLENGER
        return target

    def champion(self, model_name: str) -> ModelVersion | None:
        return next((r for r in self.records.values() if r.model_name == model_name and r.stage is DeploymentStage.CHAMPION), None)

    def compare(self, model_name: str, challenger_version: str, metric: str, higher_is_better: bool = True) -> dict[str, object]:
        champion = self.champion(model_name)
        challenger = self.records[(model_name, challenger_version)]
        if champion is None:
            return {"winner": challenger.version, "reason": "no_champion"}
        a, b = champion.metrics[metric], challenger.metrics[metric]
        challenger_wins = b > a if higher_is_better else b < a
        return {"winner": challenger.version if challenger_wins else champion.version, "champion": a, "challenger": b}

    def rollback(self, model_name: str, fallback_version: str) -> ModelVersion:
        current = self.champion(model_name)
        if current is not None:
            current.stage = DeploymentStage.ROLLED_BACK
        fallback = self.records[(model_name, fallback_version)]
        fallback.stage = DeploymentStage.CHAMPION
        self.deployment_history.append({"action": "rollback", "model": model_name, "version": fallback_version})
        return fallback


class DriftMonitor:
    def __init__(self, threshold: float = 0.2) -> None:
        self.threshold = threshold

    def evaluate(self, data_drift: float, prediction_drift: float, performance_drop: float) -> DriftReport:
        values = (data_drift, prediction_drift, performance_drop)
        if any(v < 0 for v in values):
            raise ValueError("drift metrics cannot be negative")
        return DriftReport(data_drift, prediction_drift, performance_drop, any(v >= self.threshold for v in values))
