import pytest

from app.streaming.contracts import (
    ALERTS,
    MAINTENANCE,
    TELEMETRY,
    get_contract,
    partition_key,
)
from app.streaming.metrics import StreamingMetrics


def test_streaming_topic_contracts_are_explicit() -> None:
    assert TELEMETRY.name == "redpulse.telemetry"
    assert TELEMETRY.partition_field == "machine_id"
    assert TELEMETRY.dead_letter_topic == "redpulse.telemetry.dlq"

    assert ALERTS.consumer_group == "redpulse-alert-processors"
    assert MAINTENANCE.consumer_group == "redpulse-maintenance-processors"


def test_unknown_topic_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported streaming topic"):
        get_contract("redpulse.unknown")


def test_partition_key_uses_machine_identity() -> None:
    assert (
        partition_key(
            "redpulse.telemetry",
            {"machine_id": "machine-42", "value": 12.5},
        )
        == "machine-42"
    )


def test_missing_partition_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="requires partition field"):
        partition_key(
            "redpulse.telemetry",
            {"sensor": "vibration", "value": 1.2},
        )


def test_streaming_metrics_snapshot() -> None:
    metrics = StreamingMetrics()

    metrics.record_published("redpulse.telemetry", 5)
    metrics.record_consumed(4)
    metrics.record_failure()
    metrics.record_retry(2)
    metrics.record_dead_letter()
    metrics.set_consumer_lag("redpulse-telemetry-processors", 7)

    snapshot = metrics.snapshot()

    assert snapshot.published == 5
    assert snapshot.consumed == 4
    assert snapshot.failed == 1
    assert snapshot.retried == 2
    assert snapshot.dead_lettered == 1
    assert snapshot.consumer_lag["redpulse-telemetry-processors"] == 7
    assert snapshot.topic_throughput["redpulse.telemetry"] == 5


def test_consumer_lag_cannot_be_negative() -> None:
    metrics = StreamingMetrics()

    with pytest.raises(ValueError, match="cannot be negative"):
        metrics.set_consumer_lag("group-1", -1)
