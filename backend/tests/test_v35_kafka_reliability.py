import pytest

from app.streaming.kafka import KafkaEventBus, KafkaSettings


class FakeFuture:
    pass


class FakeProducer:
    def __init__(self, failures_before_success=0):
        self.failures_before_success = failures_before_success
        self.calls = []
        self.flush_count = 0

    def send(self, topic, key=None, value=None):
        self.calls.append(
            {
                "topic": topic,
                "key": key,
                "value": value,
            }
        )

        if self.failures_before_success > 0:
            self.failures_before_success -= 1
            raise RuntimeError("broker unavailable")

        return FakeFuture()

    def flush(self):
        self.flush_count += 1


def test_kafka_publish_uses_machine_id_partition_key():
    bus = KafkaEventBus()
    producer = FakeProducer()
    bus._producer = producer

    bus.publish(
        "redpulse.telemetry",
        {
            "machine_id": "machine-101",
            "sensor": "vibration",
            "value": 4.2,
        },
    )

    assert producer.calls[0]["topic"] == "redpulse.telemetry"
    assert producer.calls[0]["key"] == "machine-101"

    snapshot = bus.metrics.snapshot()

    assert snapshot.published == 1
    assert snapshot.failed == 0


def test_kafka_publish_retries_before_success():
    bus = KafkaEventBus(
        KafkaSettings(
            max_attempts=3,
            retry_delay_seconds=0.0,
        )
    )

    producer = FakeProducer(failures_before_success=2)
    bus._producer = producer

    bus.publish(
        "redpulse.telemetry",
        {
            "machine_id": "machine-202",
            "sensor": "temperature",
            "value": 81.0,
        },
    )

    snapshot = bus.metrics.snapshot()

    assert len(producer.calls) == 3
    assert snapshot.published == 1
    assert snapshot.failed == 2
    assert snapshot.retried == 2
    assert snapshot.dead_lettered == 0


def test_kafka_publish_routes_exhausted_message_to_dlq():
    bus = KafkaEventBus(
        KafkaSettings(
            max_attempts=2,
            retry_delay_seconds=0.0,
        )
    )

    producer = FakeProducer(failures_before_success=2)
    bus._producer = producer

    with pytest.raises(RuntimeError, match="Kafka publish failed"):
        bus.publish(
            "redpulse.telemetry",
            {
                "machine_id": "machine-303",
                "sensor": "pressure",
                "value": 13.0,
            },
        )

    assert producer.calls[-1]["topic"] == "redpulse.telemetry.dlq"
    assert producer.calls[-1]["key"] == "machine-303"

    snapshot = bus.metrics.snapshot()

    assert snapshot.failed == 2
    assert snapshot.retried == 1
    assert snapshot.dead_lettered == 1
    assert snapshot.published == 1


def test_kafka_publish_rejects_missing_partition_identity():
    bus = KafkaEventBus()
    bus._producer = FakeProducer()

    with pytest.raises(ValueError, match="requires partition field"):
        bus.publish(
            "redpulse.telemetry",
            {
                "sensor": "vibration",
                "value": 1.0,
            },
        )
