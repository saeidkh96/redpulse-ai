from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True, slots=True)
class StreamingMetricsSnapshot:
    published: int
    consumed: int
    failed: int
    retried: int
    dead_lettered: int
    consumer_lag: dict[str, int]
    topic_throughput: dict[str, int]


class StreamingMetrics:
    def __init__(self) -> None:
        self._counters: defaultdict[str, int] = defaultdict(int)
        self._consumer_lag: dict[str, int] = {}
        self._topic_throughput: defaultdict[str, int] = defaultdict(int)
        self._lock = Lock()

    def record_published(self, topic: str, count: int = 1) -> None:
        with self._lock:
            self._counters["published"] += count
            self._topic_throughput[topic] += count

    def record_consumed(self, count: int = 1) -> None:
        with self._lock:
            self._counters["consumed"] += count

    def record_failure(self, count: int = 1) -> None:
        with self._lock:
            self._counters["failed"] += count

    def record_retry(self, count: int = 1) -> None:
        with self._lock:
            self._counters["retried"] += count

    def record_dead_letter(self, count: int = 1) -> None:
        with self._lock:
            self._counters["dead_lettered"] += count

    def set_consumer_lag(self, consumer_group: str, lag: int) -> None:
        if lag < 0:
            raise ValueError("Consumer lag cannot be negative")

        with self._lock:
            self._consumer_lag[consumer_group] = lag

    def snapshot(self) -> StreamingMetricsSnapshot:
        with self._lock:
            return StreamingMetricsSnapshot(
                published=self._counters["published"],
                consumed=self._counters["consumed"],
                failed=self._counters["failed"],
                retried=self._counters["retried"],
                dead_lettered=self._counters["dead_lettered"],
                consumer_lag=dict(self._consumer_lag),
                topic_throughput=dict(self._topic_throughput),
            )
