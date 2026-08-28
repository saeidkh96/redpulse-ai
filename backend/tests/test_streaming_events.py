from datetime import datetime, timezone
from app.streaming.bus import InMemoryEventBus
from app.streaming.events import TelemetryEvent
from app.services.streaming_telemetry import StreamingTelemetryService

def test_streaming_telemetry_publishes_two_events():
    bus = InMemoryEventBus()
    service = StreamingTelemetryService(bus)
    service.publish_telemetry(
        TelemetryEvent(
            machine_id="m1",
            sensor="vibration",
            value=2.5,
            timestamp=datetime.now(timezone.utc),
        )
    )
    assert len(bus.published) == 2
