from __future__ import annotations
from dataclasses import dataclass
from time import sleep
from typing import Any, Callable

@dataclass(slots=True)
class RetryPolicy:
    attempts: int = 3
    base_delay_seconds: float = 0.05

class IdempotencyStore:
    def __init__(self) -> None: self._results: dict[str, dict[str, Any]] = {}
    def get(self, key: str): return self._results.get(key)
    def put(self, key: str, result: dict[str, Any]) -> None: self._results[key] = result

class ReliableDispatcher:
    def __init__(self, policy: RetryPolicy | None = None, store: IdempotencyStore | None = None) -> None:
        self.policy, self.store = policy or RetryPolicy(), store or IdempotencyStore()

    def execute(self, key: str, operation: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        cached = self.store.get(key)
        if cached is not None: return {**cached, "idempotent_replay": True}
        last_error: Exception | None = None
        for attempt in range(1, self.policy.attempts + 1):
            try:
                result = operation()
                if result.get("ok", True):
                    result = {**result, "attempt": attempt, "idempotent_replay": False}
                    self.store.put(key, result)
                    return result
            except Exception as exc:  # adapter boundary
                last_error = exc
            if attempt < self.policy.attempts: sleep(self.policy.base_delay_seconds * attempt)
        if last_error: raise last_error
        return {"ok": False, "attempt": self.policy.attempts, "idempotent_replay": False}
