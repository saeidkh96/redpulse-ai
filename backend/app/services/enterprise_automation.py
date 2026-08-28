from __future__ import annotations
from app.automation import AutomationControlPlane, AutomationEvent, IntegrationRegistration
from app.automation.adapters import N8nAdapter, PowerAutomateAdapter, EnterpriseWebhookAdapter
from app.automation.webhooks import WebhookAdapter
from app.tenancy import MultiTenantPlatform

class EnterpriseAutomationService:
    def __init__(self) -> None:
        self.automation = AutomationControlPlane()
        self.tenancy = MultiTenantPlatform()

    def create_integration(self, tenant_id: str, name: str, provider: str, url: str, secret: str | None = None):
        webhook = WebhookAdapter(url=url, secret=secret)
        if provider == "n8n": adapter = N8nAdapter(webhook)
        elif provider == "power_automate": adapter = PowerAutomateAdapter(webhook)
        else: adapter = EnterpriseWebhookAdapter(provider, webhook)
        reg = IntegrationRegistration(name=name, provider=provider, tenant_id=tenant_id)
        self.automation.register(reg, adapter)
        return reg

    def dispatch(self, tenant_id: str, integration: str, event_type: str, entity_id: str, payload: dict):
        self.tenancy.quotas.consume_dispatch(tenant_id)
        event = AutomationEvent(event_type=event_type, entity_id=entity_id, payload=payload, tenant_id=tenant_id)
        result = self.automation.dispatch(integration, event)
        self.tenancy.audit.record(tenant_id, "integration.dispatch", "api", integration=integration, event_id=event.event_id)
        return result

enterprise_automation_service = EnterpriseAutomationService()
