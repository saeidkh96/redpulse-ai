from pydantic import BaseModel, Field


class MachineBehaviorProfilePayload(BaseModel):
    machine_id: str
    machine_type: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    dna: dict[str, float] = Field(default_factory=dict)
    operating_profile: dict[str, float] = Field(default_factory=dict)


class PeerGroupRequest(BaseModel):
    target: MachineBehaviorProfilePayload
    candidates: list[MachineBehaviorProfilePayload]
    minimum_similarity: float = Field(default=0.55, ge=0.0, le=1.0)
    limit: int = Field(default=25, ge=1, le=500)


class MachineFleetStatePayload(BaseModel):
    machine_id: str
    health_score: float = Field(ge=0.0, le=100.0)
    failure_risk: float = Field(ge=0.0, le=1.0)
    drift_score: float = Field(ge=0.0, le=1.0)
    anomaly_score: float = Field(default=0.0, ge=0.0, le=1.0)


class FleetHealthRequest(BaseModel):
    machines: list[MachineFleetStatePayload]


class FleetFailureEvidencePayload(BaseModel):
    machine_id: str
    failure_mode: str
    risk: float = Field(ge=0.0, le=1.0)
    trajectory_similarity: float = Field(ge=0.0, le=1.0)
    health_score: float = Field(ge=0.0, le=100.0)


class FleetHotspotRequest(BaseModel):
    evidence: list[FleetFailureEvidencePayload]
    minimum_risk: float = Field(default=0.40, ge=0.0, le=1.0)


class MaintenancePriorityPayload(BaseModel):
    machine_id: str
    health_score: float = Field(ge=0.0, le=100.0)
    failure_risk: float = Field(ge=0.0, le=1.0)
    drift_score: float = Field(ge=0.0, le=1.0)
    trajectory_score: float = Field(ge=0.0, le=1.0)
    counterfactual_benefit: float = Field(ge=0.0, le=1.0)
    maintenance_urgency: float = Field(ge=0.0, le=1.0)
    peer_evidence_confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class FleetPrioritizationRequest(BaseModel):
    machines: list[MaintenancePriorityPayload]
    capacity: int | None = Field(default=None, ge=1)
