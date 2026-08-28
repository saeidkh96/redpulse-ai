from app.automation.models import AutomationEvent
from app.automation.webhooks import WebhookAdapter
from app.automation.adapters import N8nAdapter, PowerAutomateAdapter
from app.automation.control_plane import AutomationControlPlane, IntegrationRegistration
from app.automation.reliability import ReliableDispatcher, RetryPolicy
from app.tenancy import MultiTenantPlatform

def fake_transport(url, body, headers, timeout): return 202, "accepted"

def test_v141_signed_webhook():
    result = WebhookAdapter("https://example.invalid/hook", "secret", transport=fake_transport).send(AutomationEvent("risk", "m1"))
    assert result["ok"] and result["status_code"] == 202

def test_v142_idempotency():
    calls = {"n": 0}; d = ReliableDispatcher(RetryPolicy(attempts=1))
    def op(): calls["n"] += 1; return {"ok": True}
    assert d.execute("same", op)["idempotent_replay"] is False
    assert d.execute("same", op)["idempotent_replay"] is True and calls["n"] == 1

def test_v143_n8n_and_v144_power_automate():
    hook = WebhookAdapter("https://example.invalid", transport=fake_transport); event = AutomationEvent("maintenance", "m1")
    assert N8nAdapter(hook).send(event)["provider"] == "n8n"
    assert PowerAutomateAdapter(hook).send(event)["provider"] == "power_automate"

def test_v150_control_plane_tenant_scoping():
    cp = AutomationControlPlane(); hook = WebhookAdapter("https://example.invalid", transport=fake_transport)
    cp.register(IntegrationRegistration("ops", "n8n", "t1"), N8nAdapter(hook))
    assert cp.dispatch("ops", AutomationEvent("alert", "m1", tenant_id="t1"))["ok"]

def test_v160_multi_tenant_rbac_and_keys():
    p = MultiTenantPlatform(); t = p.create_tenant("Plant A"); p.add_user(t.tenant_id, "alice", {"admin"})
    assert p.authorize(t.tenant_id, "alice", "manage_integrations")
    key = p.api_keys.issue(t.tenant_id); assert p.api_keys.resolve(key) == t.tenant_id
    p.audit.record(t.tenant_id, "test", "alice"); assert len(p.audit.list(t.tenant_id)) == 1
