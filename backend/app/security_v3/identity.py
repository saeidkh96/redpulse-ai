from __future__ import annotations
from dataclasses import dataclass
import hmac
import hashlib
import base64
import json
import time

@dataclass(frozen=True)
class Identity:
    subject: str
    tenant_id: str
    roles: frozenset[str]

class SignedTokenService:
    """Minimal HMAC token reference implementation, not a replacement for OIDC/JWT libraries."""
    def __init__(self, secret: str) -> None:
        if len(secret) < 16:
            raise ValueError("secret must be at least 16 characters")
        self.secret = secret.encode()

    def issue(self, identity: Identity, ttl_seconds: int = 3600) -> str:
        payload = {
            "sub": identity.subject,
            "tenant": identity.tenant_id,
            "roles": sorted(identity.roles),
            "exp": int(time.time()) + ttl_seconds,
        }
        raw = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
        sig = hmac.new(self.secret, raw.encode(), hashlib.sha256).hexdigest()
        return f"{raw}.{sig}"

    def verify(self, token: str) -> Identity:
        raw, sig = token.rsplit(".", 1)
        expected = hmac.new(self.secret, raw.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise PermissionError("invalid signature")
        padded = raw + "=" * (-len(raw) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode()))
        if payload["exp"] < int(time.time()):
            raise PermissionError("token expired")
        return Identity(payload["sub"], payload["tenant"], frozenset(payload["roles"]))
