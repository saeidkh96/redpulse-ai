from __future__ import annotations
import hashlib, hmac, json
from dataclasses import dataclass
from typing import Any, Callable
from urllib.request import Request, urlopen
from .models import AutomationEvent

Transport = Callable[[str, bytes, dict[str, str], float], tuple[int, str]]

def _http_transport(url: str, body: bytes, headers: dict[str, str], timeout: float) -> tuple[int, str]:
    req = Request(url, data=body, headers=headers, method="POST")
    with urlopen(req, timeout=timeout) as response:  # nosec B310 - URL is explicit integration configuration
        return response.status, response.read().decode("utf-8", errors="replace")

@dataclass(slots=True)
class WebhookAdapter:
    url: str
    secret: str | None = None
    timeout: float = 5.0
    transport: Transport = _http_transport

    def send(self, event: AutomationEvent) -> dict[str, Any]:
        body = json.dumps(event.to_dict(), separators=(",", ":"), sort_keys=True).encode()
        headers = {"Content-Type": "application/json", "X-RedPulse-Event-ID": event.event_id}
        if self.secret:
            signature = hmac.new(self.secret.encode(), body, hashlib.sha256).hexdigest()
            headers["X-RedPulse-Signature"] = f"sha256={signature}"
        status, text = self.transport(self.url, body, headers, self.timeout)
        return {"ok": 200 <= status < 300, "status_code": status, "response": text, "event_id": event.event_id}
