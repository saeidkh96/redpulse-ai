from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .http import JsonWebhookClient

@dataclass(slots=True)
class WorkflowInvocation:
    tenant_id: str
    workflow: str
    payload: dict[str, Any]
    correlation_id: str

class N8nRuntimeAdapter:
    def __init__(self, base_url: str, client: JsonWebhookClient | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client or JsonWebhookClient()

    def invoke(self, call: WorkflowInvocation) -> dict:
        return self.client.post(f"{self.base_url}/{call.workflow}", {
            "tenant_id": call.tenant_id,
            "correlation_id": call.correlation_id,
            "payload": call.payload,
        })

class PowerAutomateRuntimeAdapter:
    def __init__(self, flow_url: str, client: JsonWebhookClient | None = None) -> None:
        self.flow_url = flow_url
        self.client = client or JsonWebhookClient()

    def invoke(self, call: WorkflowInvocation) -> dict:
        return self.client.post(self.flow_url, {
            "tenant_id": call.tenant_id,
            "workflow": call.workflow,
            "correlation_id": call.correlation_id,
            "payload": call.payload,
        })
