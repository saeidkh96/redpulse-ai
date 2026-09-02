from __future__ import annotations

from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True, slots=True)
class BenchmarkObservation:
    latency_ms: float
    succeeded: bool = True


@dataclass(frozen=True, slots=True)
class PerformanceSLO:
    min_throughput_per_second: float
    max_p95_latency_ms: float
    max_error_rate: float = 0.01


@dataclass(frozen=True, slots=True)
class BenchmarkReport:
    requests: int
    duration_seconds: float
    throughput_per_second: float
    p95_latency_ms: float
    error_rate: float
    throughput_ok: bool
    latency_ok: bool
    error_rate_ok: bool
    ready: bool


class PerformanceBenchmarkEvaluator:
    def evaluate(
        self,
        observations: list[BenchmarkObservation],
        *,
        duration_seconds: float,
        slo: PerformanceSLO,
    ) -> BenchmarkReport:
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        if not observations:
            raise ValueError("at least one benchmark observation is required")

        latencies = sorted(max(0.0, float(item.latency_ms)) for item in observations)
        index = max(0, ceil(0.95 * len(latencies)) - 1)
        p95 = latencies[index]
        failures = sum(not item.succeeded for item in observations)
        throughput = len(observations) / duration_seconds
        error_rate = failures / len(observations)

        throughput_ok = throughput >= slo.min_throughput_per_second
        latency_ok = p95 <= slo.max_p95_latency_ms
        error_rate_ok = error_rate <= slo.max_error_rate

        return BenchmarkReport(
            requests=len(observations),
            duration_seconds=round(duration_seconds, 6),
            throughput_per_second=round(throughput, 6),
            p95_latency_ms=round(p95, 6),
            error_rate=round(error_rate, 6),
            throughput_ok=throughput_ok,
            latency_ok=latency_ok,
            error_rate_ok=error_rate_ok,
            ready=throughput_ok and latency_ok and error_rate_ok,
        )
