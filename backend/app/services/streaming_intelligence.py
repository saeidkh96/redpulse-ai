from app.streaming.topics import INTELLIGENCE_TOPIC, FLEET_TOPIC, PLANT_TOPIC

class StreamingIntelligenceService:
    def __init__(self, bus):
        self.bus = bus

    def publish_machine_event(self, event):
        self.bus.publish(INTELLIGENCE_TOPIC, event.to_dict())

    def publish_fleet_event(self, event):
        self.bus.publish(FLEET_TOPIC, event.to_dict())

    def publish_plant_event(self, event):
        self.bus.publish(PLANT_TOPIC, event.to_dict())
