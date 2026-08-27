import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.maintenance.verification import (
    MaintenanceSnapshot,
)
from app.schemas.maintenance_verification import (
    MaintenanceSnapshotRequest,
    MaintenanceSnapshotResponse,
    MaintenanceVerificationResponse,
    PostMaintenanceVerificationResponse,
)
from app.services.maintenance_verification import (
    maintenance_verification_service,
)


router = APIRouter(
    tags=["maintenance-verification"],
)


@router.post(
    "/machines/{machine_id}/maintenance-verification",
    response_model=PostMaintenanceVerificationResponse,
)
async def verify_maintenance(
    machine_id: uuid.UUID,
    body: MaintenanceSnapshotRequest,
    machine_type: str | None = Query(
        default=None,
    ),
    event_limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    library_limit: int = Query(
        default=500,
        ge=1,
        le=5000,
    ),
    session: AsyncSession = Depends(
        get_db_session
    ),
) -> PostMaintenanceVerificationResponse:
    before = MaintenanceSnapshot(
        health_score=body.health_score,
        risk_score=body.risk_score,
        deviation_score=body.deviation_score,
        drift_score=body.drift_score,
        failure_match_score=(
            body.failure_match_score
        ),
    )

    try:
        result = (
            await maintenance_verification_service.verify(
                session,
                machine_id=machine_id,
                before=before,
                machine_type=machine_type,
                event_limit=event_limit,
                library_limit=library_limit,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return PostMaintenanceVerificationResponse(
        machine_id=result.machine_id,
        before=MaintenanceSnapshotResponse(
            health_score=(
                result.before.health_score
            ),
            risk_score=(
                result.before.risk_score
            ),
            deviation_score=(
                result.before.deviation_score
            ),
            drift_score=(
                result.before.drift_score
            ),
            failure_match_score=(
                result.before.failure_match_score
            ),
        ),
        after=MaintenanceSnapshotResponse(
            health_score=(
                result.after.health_score
            ),
            risk_score=(
                result.after.risk_score
            ),
            deviation_score=(
                result.after.deviation_score
            ),
            drift_score=(
                result.after.drift_score
            ),
            failure_match_score=(
                result.after.failure_match_score
            ),
        ),
        verification=MaintenanceVerificationResponse(
            recovery_score=(
                result.verification.recovery_score
            ),
            state=result.verification.state,
            health_improvement=(
                result.verification.health_improvement
            ),
            risk_reduction=(
                result.verification.risk_reduction
            ),
            deviation_reduction=(
                result.verification.deviation_reduction
            ),
            drift_reduction=(
                result.verification.drift_reduction
            ),
            failure_match_reduction=(
                result.verification.failure_match_reduction
            ),
            components=(
                result.verification.components
            ),
        ),
    )
