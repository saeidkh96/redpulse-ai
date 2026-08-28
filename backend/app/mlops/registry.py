from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ModelVersion:
    model_name: str
    version: str
    artifact_uri: str
    framework: str
    metrics: dict[str, float] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    stage: str = "candidate"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ModelRegistry:
    def __init__(self, storage_path: str | Path = "artifacts/mlops/model_registry.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._save([])

    def register(self, model: ModelVersion) -> ModelVersion:
        records = self._load()
        if any(
            item["model_name"] == model.model_name and item["version"] == model.version
            for item in records
        ):
            raise ValueError(f"Model version already exists: {model.model_name}:{model.version}")
        records.append(asdict(model))
        self._save(records)
        return model

    def list_versions(self, model_name: str | None = None) -> list[ModelVersion]:
        records = self._load()
        if model_name is not None:
            records = [item for item in records if item["model_name"] == model_name]
        return [ModelVersion(**item) for item in records]

    def get(self, model_name: str, version: str) -> ModelVersion:
        for item in self._load():
            if item["model_name"] == model_name and item["version"] == version:
                return ModelVersion(**item)
        raise LookupError(f"Unknown model version: {model_name}:{version}")

    def transition_stage(self, model_name: str, version: str, stage: str) -> ModelVersion:
        allowed = {"candidate", "challenger", "champion", "archived"}
        if stage not in allowed:
            raise ValueError(f"Unsupported model stage: {stage}")

        records = self._load()
        updated = None
        for item in records:
            if item["model_name"] == model_name and item["version"] == version:
                item["stage"] = stage
                updated = ModelVersion(**item)
                break
        if updated is None:
            raise LookupError(f"Unknown model version: {model_name}:{version}")
        self._save(records)
        return updated

    def champion(self, model_name: str) -> ModelVersion | None:
        champions = [
            ModelVersion(**item)
            for item in self._load()
            if item["model_name"] == model_name and item["stage"] == "champion"
        ]
        return champions[-1] if champions else None

    def _load(self) -> list[dict]:
        try:
            return json.loads(self.storage_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Corrupt model registry: {self.storage_path}") from exc

    def _save(self, records: list[dict]) -> None:
        self.storage_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
