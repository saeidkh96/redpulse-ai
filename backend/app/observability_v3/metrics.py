from __future__ import annotations
from collections import defaultdict
import time

class MetricsRegistry:
    def __init__(self) -> None:
        self.counters = defaultdict(int)
        self.timings = defaultdict(list)

    def inc(self, name: str, value: int = 1) -> None:
        self.counters[name] += value

    def observe_ms(self, name: str, value: float) -> None:
        self.timings[name].append(value)

    def snapshot(self) -> dict:
        return {
            "counters": dict(self.counters),
            "timings": {k: list(v) for k, v in self.timings.items()},
        }

class Timer:
    def __init__(self, registry: MetricsRegistry, name: str) -> None:
        self.registry = registry
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.registry.observe_ms(self.name, (time.perf_counter() - self.start) * 1000)
