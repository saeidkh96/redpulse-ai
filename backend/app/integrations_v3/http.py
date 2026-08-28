from __future__ import annotations
from urllib import request
import json

class JsonWebhookClient:
    def post(self, url: str, payload: dict, headers: dict[str, str] | None = None, timeout: float = 10.0) -> dict:
        body = json.dumps(payload).encode()
        req = request.Request(url, data=body, headers={"Content-Type": "application/json", **(headers or {})})
        with request.urlopen(req, timeout=timeout) as resp:
            return {"status": resp.status, "body": resp.read().decode(errors="replace")}
