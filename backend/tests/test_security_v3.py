from app.security_v3.identity import SignedTokenService, Identity
from app.security_v3.policy import TenantPolicy, AuthorizationContext

def test_signed_token_roundtrip():
    svc = SignedTokenService("1234567890abcdef")
    token = svc.issue(Identity("u1", "t1", frozenset({"engineer"})))
    identity = svc.verify(token)
    assert identity.subject == "u1"
    assert identity.tenant_id == "t1"

def test_policy():
    policy = TenantPolicy()
    ctx = AuthorizationContext("t1", frozenset({"approver"}))
    assert policy.allowed(ctx, "approve")
    assert not policy.allowed(ctx, "propose")
