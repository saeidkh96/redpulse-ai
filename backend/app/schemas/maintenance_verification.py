import uuid

from pydantic import BaseModel

from app.maintenance.verification import (
    RecoveryState,
)


class MaintenanceSnapshotRequest(BaseModel):
    health_score: float
    risk_score: float
    deviation_score: float
    drift_score: float
    failure_match_score: float


class MaintenanceSnapshotResponse(BaseModel):
    health_score: float
    risk_score: float
    deviation_score: float
    drift_score: float
    failure_match_score: float


class MaintenanceVerificationResponse(BaseModel):
    recovery_score: float
    state: RecoveryState
    health_improvement: float
    risk_reduction: float
    deviation_reduction: float
    drift_reduction: float
    failure_match_reduction: float
    components: dict[str, float]


class PostMaintenanceVerificationResponse(BaseModel):
    machine_id: uuid.UUID
    before: MaintenanceSnapshotResponse
    after: MaintenanceSnapshotResponse
    verification: MaintenanceVerificationResponse
