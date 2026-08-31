from __future__ import annotations

import json
import time
from dataclasses import dataclass

from app.streaming.bus import EventBus
from app.streaming.contracts import get_contract, partition_key
from app.streaming.metrics import StreamingMetrics


@dataclass(frozen=True)
class KafkaSettings:
    bootstrap_servers: str = "localhost:9092"
    client_id: str = "redpulse-ai"
    max_attempts: int = 3
    retry_delay_seconds: float = 0.05


class KafkaEventBus(EventBus):
    def __init__(self, settings=None, metrics=None):
        self.settings = settings or KafkaSettings()
        self.metrics = metrics or StreamingMetrics()
        self._producer = None
        self._subscriptions = []

    def _get_producer(self):
        if self._producer is None:
            try:
                from kafka import KafkaProducer
            except ImportError as exc:
                raise RuntimeError(
                    "Install backend/requirements-streaming.txt for Kafka support."
                ) from exc

            self._producer = KafkaProducer(
                bootstrap_servers=self.settings.bootstrap_servers,
                client_id=self.settings.client_id,
                key_serializer=lambda value: value.encode("utf-8"),
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            )

        return self._producer

    def publish(self, topic, event):
        contract = get_contract(topic)
        key = partition_key(topic, event)
        producer = self._get_producer()

        last_error = None

        for attempt in range(1, self.settings.max_attempts + 1):
            try:
                producer.send(topic, key=key, value=event)
                producer.flush()
                self.metrics.record_published(topic)
                return
            except Exception as exc:
                last_error = exc
                self.metrics.record_failure()

                if attempt < self.settings.max_attempts:
                    self.metrics.record_retry()
                    time.sleep(self.settings.retry_delay_seconds)

        self._publish_dead_letter(
            producer=producer,
            topic=contract.dead_letter_topic,
            key=key,
            event=event,
            error=last_error,
        )

        raise RuntimeError(
            f"Kafka publish failed after {self.settings.max_attempts} attempts"
        ) from last_error

    def _publish_dead_letter(self, producer, topic, key, event, error):
        envelope = {
            "original_event": event,
            "error": str(error) if error else "unknown",
        }

        producer.send(topic, key=key, value=envelope)
        producer.flush()

        self.metrics.record_dead_letter()
        self.metrics.record_published(topic)

    def subscribe(self, topic, handler):
        self._subscriptions.append((topic, handler))

    def consume_forever(self, topic, group_id=None, handler=None):
        try:
            from kafka import KafkaConsumer
        except ImportError as exc:
            raise RuntimeError(
                "Install backend/requirements-streaming.txt for Kafka support."
            ) from exc

        contract = get_contract(topic)
        resolved_group_id = group_id or contract.consumer_group

        if handler is None:
            raise ValueError("Kafka consumer requires a handler")

        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.settings.bootstrap_servers,
            group_id=resolved_group_id,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )

        for message in consumer:
            try:
                handler(message.value)
                self.metrics.record_consumed()
            except Exception:
                self.metrics.record_failure()
                raise
