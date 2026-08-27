import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.maintenance.verification import MaintenanceSnapshot
from app.schemas.maintenance_history import (
    LearnedInterventionProfileResponse,
    MaintenanceCompletionResponse,
    MaintenanceInterventionCreate,
    MaintenanceInterventionResponse,
)
from app.schemas.maintenance_verification import (
    MaintenanceSnapshotResponse,
    MaintenanceVerificationResponse,
)
from app.services.maintenance_history import maintenance_history_service
from app.services.maintenance_outcome import maintenance_outcome_service


router = APIRouter(tags=["maintenance-history"])


@router.post(
    "/machines/{machine_id}/maintenance-interventions",
    response_model=MaintenanceInterventionResponse,
)
async def create_intervention(
    machine_id: uuid.UUID,
    body: MaintenanceInterventionCreate,
    session: AsyncSession = Depends(get_db_session),
) -> MaintenanceInterventionResponse:
    before = MaintenanceSnapshot(
        health_score=body.before_snapshot.health_score,
        risk_score=body.before_snapshot.risk_score,
        deviation_score=body.before_snapshot.deviation_score,
        drift_score=body.before_snapshot.drift_score,
        failure_match_score=body.before_snapshot.failure_match_score,
    )
    record = await maintenance_history_service.create(
        session,
        machine_id=machine_id,
        machine_type=body.machine_type,
        intervention_type=body.intervention_type,
        failure_prediction=body.failure_prediction,
        recommendation=body.recommendation,
        technician_notes=body.technician_notes,
        before=before,
        started_at=body.started_at,
    )
    return MaintenanceInterventionResponse.model_validate(record)


@router.get(
    "/machines/{machine_id}/maintenance-interventions",
    response_model=list[MaintenanceInterventionResponse],
)
async def list_interventions(
    machine_id: uuid.UUID,
    limit: int = Query(default=100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db_session),
) -> list[MaintenanceInterventionResponse]:
    records = await maintenance_history_service.list_for_machine(
        session, machine_id=machine_id, limit=limit
    )
    return [MaintenanceInterventionResponse.model_validate(x) for x in records]


@router.get(
    "/maintenance-interventions/{intervention_id}",
    response_model=MaintenanceInterventionResponse,
)
async def get_intervention(
    intervention_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> MaintenanceInterventionResponse:
    try:
        record = await maintenance_history_service.get(session, intervention_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return MaintenanceInterventionResponse.model_validate(record)


@router.post(
    "/maintenance-interventions/{intervention_id}/complete",
    response_model=MaintenanceCompletionResponse,
)
async def complete_intervention(
    intervention_id: uuid.UUID,
    event_limit: int = Query(default=100, ge=1, le=1000),
    library_limit: int = Query(default=500, ge=1, le=5000),
    session: AsyncSession = Depends(get_db_session),
) -> MaintenanceCompletionResponse:
    try:
        record, result = await maintenance_history_service.complete_and_verify(
            session,
            intervention_id=intervention_id,
            event_limit=event_limit,
            library_limit=library_limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return MaintenanceCompletionResponse(
        intervention=MaintenanceInterventionResponse.model_validate(record),
        before=MaintenanceSnapshotResponse(
            health_score=result.before.health_score,
            risk_score=result.before.risk_score,
            deviation_score=result.before.deviation_score,
            drift_score=result.before.drift_score,
            failure_match_score=result.before.failure_match_score,
        ),
        after=MaintenanceSnapshotResponse(
            health_score=result.after.health_score,
            risk_score=result.after.risk_score,
            deviation_score=result.after.deviation_score,
            drift_score=result.after.drift_score,
            failure_match_score=result.after.failure_match_score,
        ),
        verification=MaintenanceVerificationResponse(
            recovery_score=result.verification.recovery_score,
            state=result.verification.state,
            health_improvement=result.verification.health_improvement,
            risk_reduction=result.verification.risk_reduction,
            deviation_reduction=result.verification.deviation_reduction,
            drift_reduction=result.verification.drift_reduction,
            failure_match_reduction=result.verification.failure_match_reduction,
            components=result.verification.components,
        ),
    )


@router.get(
    "/maintenance-outcomes",
    response_model=list[LearnedInterventionProfileResponse],
)
async def learned_outcomes(
    machine_id: uuid.UUID | None = Query(default=None),
    machine_type: str | None = Query(default=None),
    intervention_type: str | None = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=5000),
    session: AsyncSession = Depends(get_db_session),
) -> list[LearnedInterventionProfileResponse]:
    profiles = await maintenance_outcome_service.learn(
        session,
        machine_id=machine_id,
        machine_type=machine_type,
        intervention_type=intervention_type,
        limit=limit,
    )
    return [
        LearnedInterventionProfileResponse(
            intervention_type=x.intervention_type,
            sample_count=x.sample_count,
            average_recovery_score=x.average_recovery_score,
            average_risk_reduction=x.average_risk_reduction,
            average_drift_reduction=x.average_drift_reduction,
            average_health_improvement=x.average_health_improvement,
            success_rate=x.success_rate,
            confidence=x.confidence,
            state=x.state,
        )
        for x in profiles
    ]
