from __future__ import annotations
import time
from contextlib import contextmanager

class OperationMetrics:
    def __init__(self) -> None:
        self.counters: dict[str, int] = {}
        self.latency_ms: dict[str, list[float]] = {}

    def inc(self, name: str) -> None:
        self.counters[name] = self.counters.get(name, 0) + 1

    @contextmanager
    def timer(self, name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            self.latency_ms.setdefault(name, []).append(elapsed)
