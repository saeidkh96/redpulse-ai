from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class ObservabilitySnapshot:
    counters: dict[str, int]


class MLOpsObservability:
    def __init__(self) -> None:
        self._counters: Counter[str] = Counter()

    def increment(self, metric: str, value: int = 1) -> None:
        self._counters[metric] += value

    def snapshot(self) -> ObservabilitySnapshot:
        return ObservabilitySnapshot(counters=dict(self._counters))
