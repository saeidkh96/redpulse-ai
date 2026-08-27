import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.failure_explanation import (
    ExplanationEvidenceResponse,
    FailureExplanationResponse,
    MachineFailureExplanationResponse,
    RootCauseHintResponse,
)
from app.schemas.failure_prediction import (
    FailurePredictionResponse,
    FailureRiskResponse,
)
from app.services.failure_explanation import (
    failure_explanation_service,
)


router = APIRouter(
    tags=["failure-explanation"],
)


@router.get(
    "/machines/{machine_id}/failure-explanation",
    response_model=MachineFailureExplanationResponse,
)
async def get_failure_explanation(
    machine_id: uuid.UUID,
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
) -> MachineFailureExplanationResponse:
    try:
        result = (
            await failure_explanation_service.explain(
                session,
                machine_id=machine_id,
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

    prediction = result.prediction
    explanation = result.explanation

    prediction_response = FailurePredictionResponse(
        machine_id=str(
            prediction.machine_id
        ),
        likely_failure_type=(
            prediction.likely_failure_type
        ),
        likely_failure_title=(
            prediction.likely_failure_title
        ),
        risk=FailureRiskResponse(
            risk_score=(
                prediction.risk.risk_score
            ),
            confidence=(
                prediction.risk.confidence
            ),
            level=prediction.risk.level.value,
            trend=prediction.risk.trend.value,
            components=(
                prediction.risk.components
            ),
        ),
        historical_match_confidence=(
            prediction
            .historical_match_confidence
        ),
        failure_match_score=(
            prediction.failure_match_score
        ),
        evidence=prediction.evidence,
    )

    explanation_response = FailureExplanationResponse(
        summary=explanation.summary,
        primary_driver=(
            explanation.primary_driver
        ),
        evidence=[
            ExplanationEvidenceResponse(
                category=item.category,
                name=item.name,
                contribution=(
                    item.contribution
                ),
                value=item.value,
                description=item.description,
            )
            for item in explanation.evidence
        ],
        root_cause_hints=[
            RootCauseHintResponse(
                cause=item.cause,
                confidence=item.confidence,
                supporting_evidence=(
                    item.supporting_evidence
                ),
            )
            for item
            in explanation.root_cause_hints
        ],
    )

    return MachineFailureExplanationResponse(
        machine_id=result.machine_id,
        prediction=prediction_response,
        explanation=explanation_response,
    )
