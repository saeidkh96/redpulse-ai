from __future__ import annotations
import time
from typing import Callable, Any
from .models import RuntimeRecord, RuntimeStatus
from .persistence import JsonRuntimeRepository

class PersistentJobRuntime:
    def __init__(self, repository: JsonRuntimeRepository | None = None, max_attempts: int = 3) -> None:
        self.repository = repository or JsonRuntimeRepository()
        self.max_attempts = max_attempts

    def submit(self, tenant_id: str, kind: str, payload: dict) -> RuntimeRecord:
        return self.repository.save(RuntimeRecord.create(tenant_id, kind, payload))

    def run(self, record_id: str, handler: Callable[[RuntimeRecord], Any]) -> RuntimeRecord:
        record = self.repository.get(record_id)
        while record.attempts < self.max_attempts:
            record.status = RuntimeStatus.RUNNING
            record.attempts += 1
            record.updated_at = time.time()
            self.repository.save(record)
            try:
                result = handler(record)
                record.payload["result"] = result
                record.status = RuntimeStatus.SUCCEEDED
                record.updated_at = time.time()
                return self.repository.save(record)
            except Exception as exc:
                record.payload["last_error"] = str(exc)
                record.status = RuntimeStatus.FAILED
                record.updated_at = time.time()
                self.repository.save(record)
        record.status = RuntimeStatus.DEAD
        return self.repository.save(record)
