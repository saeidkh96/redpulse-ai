from __future__ import annotations
import json
from pathlib import Path
from threading import RLock
from .models import RuntimeRecord, RuntimeStatus

class JsonRuntimeRepository:
    """Small persistent repository used as a restart-safe local reference implementation."""
    def __init__(self, path: str | Path = "artifacts/runtime_v3/runtime.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _read(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8") or "{}")

    def _write(self, data: dict) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.path)

    def save(self, record: RuntimeRecord) -> RuntimeRecord:
        with self._lock:
            data = self._read()
            data[record.record_id] = {
                "record_id": record.record_id,
                "tenant_id": record.tenant_id,
                "kind": record.kind,
                "status": record.status.value,
                "payload": record.payload,
                "attempts": record.attempts,
                "created_at": record.created_at,
                "updated_at": record.updated_at,
            }
            self._write(data)
            return record

    def get(self, record_id: str) -> RuntimeRecord:
        item = self._read()[record_id]
        return RuntimeRecord(
            record_id=item["record_id"],
            tenant_id=item["tenant_id"],
            kind=item["kind"],
            status=RuntimeStatus(item["status"]),
            payload=item.get("payload", {}),
            attempts=item.get("attempts", 0),
            created_at=item["created_at"],
            updated_at=item["updated_at"],
        )

    def list_tenant(self, tenant_id: str) -> list[RuntimeRecord]:
        return [self.get(rid) for rid, item in self._read().items() if item["tenant_id"] == tenant_id]
