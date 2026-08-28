from fastapi import APIRouter, HTTPException
from app.schemas.enterprise_automation import TenantCreateRequest, UserCreateRequest, IntegrationCreateRequest, DispatchRequest
from app.services.enterprise_automation import enterprise_automation_service as service

router = APIRouter(prefix="/enterprise-automation", tags=["Enterprise Automation"])

@router.post("/tenants")
def create_tenant(body: TenantCreateRequest):
    tenant = service.tenancy.create_tenant(body.name)
    return {"tenant_id": tenant.tenant_id, "name": tenant.name, "active": tenant.active}

@router.post("/tenants/{tenant_id}/users")
def add_user(tenant_id: str, body: UserCreateRequest):
    try: user = service.tenancy.add_user(tenant_id, body.user_id, set(body.roles))
    except KeyError as exc: raise HTTPException(404, "tenant not found") from exc
    return {"tenant_id": user.tenant_id, "user_id": user.user_id, "roles": sorted(user.roles)}

@router.post("/integrations")
def create_integration(body: IntegrationCreateRequest):
    reg = service.create_integration(body.tenant_id, body.name, body.provider, body.url, body.secret)
    return {"name": reg.name, "provider": reg.provider, "tenant_id": reg.tenant_id, "enabled": reg.enabled}

@router.get("/tenants/{tenant_id}/integrations")
def list_integrations(tenant_id: str):
    return [{"name": r.name, "provider": r.provider, "enabled": r.enabled} for r in service.automation.list(tenant_id)]

@router.post("/dispatch")
def dispatch(body: DispatchRequest):
    try: return service.dispatch(body.tenant_id, body.integration, body.event_type, body.entity_id, body.payload)
    except KeyError as exc: raise HTTPException(404, str(exc)) from exc
    except PermissionError as exc: raise HTTPException(403, str(exc)) from exc

@router.get("/tenants/{tenant_id}/audit")
def audit(tenant_id: str): return service.tenancy.audit.list(tenant_id)
