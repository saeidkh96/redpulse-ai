from __future__ import annotations
import hashlib
import json

def idempotency_key(namespace: str, payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    return f"{namespace}:{digest}"
