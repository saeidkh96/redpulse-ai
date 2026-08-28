import json
from dataclasses import dataclass
from app.streaming.bus import EventBus

@dataclass(frozen=True)
class KafkaSettings:
    bootstrap_servers: str = "localhost:9092"
    client_id: str = "redpulse-ai"

class KafkaEventBus(EventBus):
    def __init__(self, settings=None):
        self.settings = settings or KafkaSettings()
        self._producer = None
        self._subscriptions = []

    def _get_producer(self):
        if self._producer is None:
            try:
                from kafka import KafkaProducer
            except ImportError as exc:
                raise RuntimeError("Install backend/requirements-streaming.txt for Kafka support.") from exc
            self._producer = KafkaProducer(
                bootstrap_servers=self.settings.bootstrap_servers,
                client_id=self.settings.client_id,
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            )
        return self._producer

    def publish(self, topic, event):
        producer = self._get_producer()
        producer.send(topic, event)
        producer.flush()

    def subscribe(self, topic, handler):
        self._subscriptions.append((topic, handler))

    def consume_forever(self, topic, group_id, handler):
        try:
            from kafka import KafkaConsumer
        except ImportError as exc:
            raise RuntimeError("Install backend/requirements-streaming.txt for Kafka support.") from exc
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.settings.bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
            auto_offset_reset="earliest",
        )
        for message in consumer:
            handler(message.value)
