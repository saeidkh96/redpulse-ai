from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FeatureStore:
    def __init__(self, storage_path: str | Path = "artifacts/mlops/feature_store.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("{}", encoding="utf-8")

    def put(self, entity_id: str, feature_group: str, features: dict[str, Any]) -> None:
        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        data.setdefault(entity_id, {})[feature_group] = features
        self.storage_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get(self, entity_id: str, feature_group: str) -> dict[str, Any]:
        data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        try:
            return data[entity_id][feature_group]
        except KeyError as exc:
            raise LookupError(f"Unknown feature group: {entity_id}:{feature_group}") from exc
