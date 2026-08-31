from __future__ import annotations

from dataclasses import dataclass

from app.streaming.metrics import StreamingMetrics, StreamingMetricsSnapshot


@dataclass(frozen=True, slots=True)
class StreamingHealth:
    status: str
    ready: bool
    published: int
    consumed: int
    failed: int
    retried: int
    dead_lettered: int
    total_consumer_lag: int


class StreamingHealthService:
    def __init__(self, metrics: StreamingMetrics) -> None:
        self.metrics = metrics

    def snapshot(self) -> StreamingHealth:
        metrics: StreamingMetricsSnapshot = self.metrics.snapshot()
        total_lag = sum(metrics.consumer_lag.values())

        degraded = (
            metrics.failed > 0
            or metrics.dead_lettered > 0
            or total_lag > 100
        )

        return StreamingHealth(
            status="degraded" if degraded else "ok",
            ready=not degraded,
            published=metrics.published,
            consumed=metrics.consumed,
            failed=metrics.failed,
            retried=metrics.retried,
            dead_lettered=metrics.dead_lettered,
            total_consumer_lag=total_lag,
        )
