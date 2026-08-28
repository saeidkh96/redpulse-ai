from pydantic import BaseModel, Field
from typing import Any

class KnowledgeIngestRequest(BaseModel):
    source_id: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class CopilotRequest(BaseModel):
    machine_id: str
    question: str
    machine_dna: dict[str, Any] = Field(default_factory=dict)
    telemetry: dict[str, Any] = Field(default_factory=dict)
    health: dict[str, Any] = Field(default_factory=dict)
    failure_risk: dict[str, Any] = Field(default_factory=dict)
    maintenance_history: list[dict[str, Any]] = Field(default_factory=list)

class AgentRunRequest(BaseModel):
    objective: str

class ApprovalRequest(BaseModel):
    actor: str

class DispatchRequest(BaseModel):
    adapter: str
    event_type: str
    entity_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
