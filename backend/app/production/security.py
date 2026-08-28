from dataclasses import dataclass
import hashlib, hmac, os, time

@dataclass(frozen=True, slots=True)
class ServiceIdentity:
    tenant_id: str
    subject: str
    scopes: frozenset[str]

class TenantAuthorizer:
    @staticmethod
    def require(identity: ServiceIdentity, tenant_id: str, scope: str) -> None:
        if identity.tenant_id != tenant_id: raise PermissionError("cross-tenant access denied")
        if scope not in identity.scopes: raise PermissionError(f"missing scope: {scope}")

class EnvironmentSecretResolver:
    def resolve(self, reference: str) -> str:
        if not reference.startswith("env://"): raise ValueError("only env:// secret references are supported")
        key=reference.removeprefix("env://")
        value=os.getenv(key)
        if not value: raise KeyError(f"secret not configured: {key}")
        return value

class WebhookSigner:
    @staticmethod
    def sign(secret: str, body: bytes, timestamp: int | None=None) -> tuple[str,int]:
        ts=timestamp or int(time.time()); msg=f"{ts}.".encode()+body
        return hmac.new(secret.encode(),msg,hashlib.sha256).hexdigest(),ts
