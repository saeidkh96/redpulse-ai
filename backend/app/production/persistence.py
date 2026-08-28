from dataclasses import asdict
from pathlib import Path
import json

class SnapshotRepository:
    """Small persistence boundary for control-plane state; replaceable by DB adapters."""
    def __init__(self, path: str | Path): self.path=Path(path)
    def load(self) -> dict:
        if not self.path.exists(): return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
    def save(self, value: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp=self.path.with_suffix(self.path.suffix+".tmp")
        tmp.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.path)
