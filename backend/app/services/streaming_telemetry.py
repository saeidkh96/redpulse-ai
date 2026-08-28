from app.streaming.events import IntelligenceEvent, IntelligenceEventType
from app.streaming.topics import TELEMETRY_TOPIC, INTELLIGENCE_TOPIC

class StreamingTelemetryService:
    def __init__(self, bus):
        self.bus = bus

    def publish_telemetry(self, event):
        self.bus.publish(TELEMETRY_TOPIC, event.to_dict())
        self.bus.publish(
            INTELLIGENCE_TOPIC,
            IntelligenceEvent(
                event_type=IntelligenceEventType.TELEMETRY_INGESTED,
                entity_id=event.machine_id,
                score=1.0,
                payload={"sensor": event.sensor, "value": event.value},
            ).to_dict(),
        )
