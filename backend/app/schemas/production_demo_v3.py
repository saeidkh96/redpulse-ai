from pydantic import BaseModel, Field

class DemoRunRequest(BaseModel):
    tenant_id: str
    machine_id: str
    signals: dict[str, float] = Field(default_factory=dict)

class TokenIssueRequest(BaseModel):
    subject: str
    tenant_id: str
    roles: list[str] = Field(default_factory=list)
