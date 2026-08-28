from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ExperimentRun:
    experiment_name: str
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExperimentTracker:
    def __init__(self, storage_path: str | Path = "artifacts/mlops/experiments.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("[]", encoding="utf-8")

    def log_run(self, run: ExperimentRun) -> ExperimentRun:
        records = json.loads(self.storage_path.read_text(encoding="utf-8"))
        records.append(asdict(run))
        self.storage_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        return run

    def list_runs(self, experiment_name: str | None = None) -> list[ExperimentRun]:
        records = json.loads(self.storage_path.read_text(encoding="utf-8"))
        if experiment_name is not None:
            records = [item for item in records if item["experiment_name"] == experiment_name]
        return [ExperimentRun(**item) for item in records]
