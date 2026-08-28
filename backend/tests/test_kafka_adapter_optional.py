from app.streaming.kafka import KafkaEventBus, KafkaSettings

def test_kafka_adapter_can_be_constructed_without_dependency_import():
    bus = KafkaEventBus(KafkaSettings(bootstrap_servers="localhost:9092"))
    assert bus.settings.bootstrap_servers == "localhost:9092"
