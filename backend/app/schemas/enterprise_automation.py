from typing import Any
from pydantic import BaseModel, Field

class TenantCreateRequest(BaseModel): name: str = Field(min_length=1, max_length=120)
class UserCreateRequest(BaseModel): user_id: str; roles: list[str] = []
class IntegrationCreateRequest(BaseModel):
    tenant_id: str
    name: str
    provider: str
    url: str
    secret: str | None = None
class DispatchRequest(BaseModel):
    tenant_id: str
    integration: str
    event_type: str
    entity_id: str
    payload: dict[str, Any] = {}
