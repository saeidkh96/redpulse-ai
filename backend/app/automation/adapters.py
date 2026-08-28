from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .models import AutomationEvent
from .webhooks import WebhookAdapter

@dataclass(slots=True)
class N8nAdapter:
    webhook: WebhookAdapter
    def send(self, event: AutomationEvent) -> dict[str, Any]:
        return {**self.webhook.send(event), "provider": "n8n"}

@dataclass(slots=True)
class PowerAutomateAdapter:
    webhook: WebhookAdapter
    def send(self, event: AutomationEvent) -> dict[str, Any]:
        return {**self.webhook.send(event), "provider": "power_automate"}

@dataclass(slots=True)
class EnterpriseWebhookAdapter:
    provider: str
    webhook: WebhookAdapter
    def send(self, event: AutomationEvent) -> dict[str, Any]:
        return {**self.webhook.send(event), "provider": self.provider}

SUPPORTED_ENTERPRISE_TARGETS = ("jira", "slack", "teams", "outlook", "email", "planner", "sharepoint", "cmms", "erp")
