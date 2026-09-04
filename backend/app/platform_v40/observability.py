from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlatformMetrics:
    gauges: dict[str, float] = field(default_factory=dict)
    counters: dict[str, int] = field(default_factory=dict)

    REQUIRED_GAUGES = (
        "machine_health_score",
        "failure_probability",
        "model_drift_score",
        "prediction_latency_ms",
        "kafka_consumer_lag",
    )
    REQUIRED_COUNTERS = (
        "anomaly_events_total",
        "maintenance_success_total",
        "integration_delivery_failure_total",
    )

    def set_gauge(self, name: str, value: float) -> None:
        self.gauges[name] = float(value)

    def increment(self, name: str, amount: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + amount

    def coverage(self) -> dict[str, object]:
        missing = [name for name in self.REQUIRED_GAUGES if name not in self.gauges]
        missing += [name for name in self.REQUIRED_COUNTERS if name not in self.counters]
        return {"complete": not missing, "missing": missing}
