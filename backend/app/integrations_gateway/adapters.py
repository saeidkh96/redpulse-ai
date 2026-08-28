from __future__ import annotations
from urllib import request
import json
from .gateway import IntegrationEvent

class WebhookAdapter:
    def __init__(self, url: str, timeout: float = 5.0) -> None:
        self.url = url
        self.timeout = timeout

    def send(self, event: IntegrationEvent) -> dict:
        body = json.dumps({
            "event_type": event.event_type,
            "entity_id": event.entity_id,
            "payload": event.payload,
        }).encode()
        req = request.Request(self.url, data=body, headers={"Content-Type": "application/json"})
        with request.urlopen(req, timeout=self.timeout) as response:
            return {"status": response.status, "adapter": "webhook"}

class N8nAdapter(WebhookAdapter):
    pass

class PowerAutomateAdapter(WebhookAdapter):
    pass
