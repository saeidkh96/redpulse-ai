from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac
import json
from typing import Callable


class IntegrationAdapter(str, Enum):
    WEBHOOK = "webhook"
    N8N = "n8n"
    POWER_AUTOMATE = "power_automate"
    TEAMS = "teams"
    EMAIL = "email"
    JIRA = "jira"


@dataclass(frozen=True)
class DeliveryRequest:
    adapter: IntegrationAdapter
    tenant_id: str
    event_type: str
    idempotency_key: str
    payload: dict


@dataclass
class DeliveryReceipt:
    adapter: IntegrationAdapter
    idempotency_key: str
    delivered: bool
    attempts: int
    response: object | None = None
    error: str | None = None


class SignedWebhook:
    @staticmethod
    def sign(payload: dict, secret: str) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()

    @staticmethod
    def verify(payload: dict, secret: str, signature: str) -> bool:
        return hmac.compare_digest(SignedWebhook.sign(payload, secret), signature)


class EnterpriseIntegrationGateway:
    def __init__(self, max_attempts: int = 3) -> None:
        self.max_attempts = max_attempts
        self.adapters: dict[IntegrationAdapter, Callable[[DeliveryRequest], object]] = {}
        self.receipts: list[DeliveryReceipt] = []
        self._delivered: dict[str, DeliveryReceipt] = {}

    def register(self, adapter: IntegrationAdapter, sender: Callable[[DeliveryRequest], object]) -> None:
        self.adapters[adapter] = sender

    def dispatch(self, request: DeliveryRequest) -> DeliveryReceipt:
        if not request.idempotency_key:
            raise ValueError("idempotency_key is required")
        if request.idempotency_key in self._delivered:
            return self._delivered[request.idempotency_key]
        if request.adapter not in self.adapters:
            raise KeyError(request.adapter)
        last_error: str | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.adapters[request.adapter](request)
                receipt = DeliveryReceipt(request.adapter, request.idempotency_key, True, attempt, response=response)
                self.receipts.append(receipt)
                self._delivered[request.idempotency_key] = receipt
                return receipt
            except Exception as exc:
                last_error = str(exc)
        receipt = DeliveryReceipt(request.adapter, request.idempotency_key, False, self.max_attempts, error=last_error)
        self.receipts.append(receipt)
        return receipt
