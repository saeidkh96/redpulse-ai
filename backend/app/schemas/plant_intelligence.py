from pydantic import BaseModel, Field


class PlantFleetPayload(BaseModel):
    site_id: str
    fleet_id: str
    fleet_health_score: float = Field(ge=0.0, le=100.0)
    fleet_risk_score: float = Field(ge=0.0, le=1.0)
    critical_machine_count: int = Field(ge=0)
    degraded_machine_count: int = Field(ge=0)
    machine_count: int = Field(ge=0)
    maintenance_backlog: int = Field(default=0, ge=0)


class PlantIntelligenceRequest(BaseModel):
    fleets: list[PlantFleetPayload]


class FleetEarlyWarningPayload(BaseModel):
    fleet_id: str
    current_risk: float = Field(ge=0.0, le=1.0)
    previous_risk: float = Field(ge=0.0, le=1.0)
    current_health: float = Field(ge=0.0, le=100.0)
    previous_health: float = Field(ge=0.0, le=100.0)
    critical_machine_ratio: float = Field(ge=0.0, le=1.0)
    hotspot_severity: float = Field(ge=0.0, le=1.0)
    drift_pressure: float = Field(ge=0.0, le=1.0)
    maintenance_backlog_ratio: float = Field(default=0.0, ge=0.0, le=1.0)


class FleetEarlyWarningRequest(BaseModel):
    fleets: list[FleetEarlyWarningPayload]


class FleetRiskObservationPayload(BaseModel):
    step: int
    risk_score: float = Field(ge=0.0, le=1.0)
    health_score: float = Field(ge=0.0, le=100.0)
    drift_pressure: float = Field(ge=0.0, le=1.0)
    hotspot_severity: float = Field(ge=0.0, le=1.0)


class FleetRiskForecastRequest(BaseModel):
    observations: list[FleetRiskObservationPayload]
    horizon_steps: int = Field(default=5, ge=1, le=30)


class PlantMaintenancePayload(BaseModel):
    site_id: str
    fleet_id: str
    machine_id: str
    fleet_priority_score: float = Field(ge=0.0, le=1.0)
    fleet_warning_score: float = Field(ge=0.0, le=1.0)
    forecast_risk: float = Field(ge=0.0, le=1.0)
    counterfactual_benefit: float = Field(ge=0.0, le=1.0)
    maintenance_urgency: float = Field(ge=0.0, le=1.0)
    expected_downtime_hours: float = Field(ge=0.0)
    available_capacity_units: float = Field(default=1.0, ge=0.0)


class PlantMaintenanceRequest(BaseModel):
    items: list[PlantMaintenancePayload]
    capacity_by_site: dict[str, float]
