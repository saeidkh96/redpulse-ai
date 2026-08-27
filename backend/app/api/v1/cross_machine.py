import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.cross_machine import (
    CrossMachineAnalysisRequest,
    CrossMachineAnalysisResponse,
    CrossMachineInterventionEvidenceResponse,
    CrossMachineRecommendationResponse,
)
from app.services.cross_machine import cross_machine_learning_service


router = APIRouter(tags=["cross-machine-learning"])


@router.post(
    "/machines/{machine_id}/cross-machine-learning",
    response_model=CrossMachineAnalysisResponse,
)
async def analyze_cross_machine_learning(
    machine_id: uuid.UUID,
    payload: CrossMachineAnalysisRequest,
    session: AsyncSession = Depends(get_db_session),
) -> CrossMachineAnalysisResponse:
    try:
        result = await cross_machine_learning_service.analyze(
            session,
            machine_id=machine_id,
            peer_limit=payload.peer_limit,
            history_limit=payload.history_limit,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    recommendation = result.recommendation
    interventions = []
    for item in recommendation.interventions:
        profile = item.historical_profile
        interventions.append(
            CrossMachineInterventionEvidenceResponse(
                intervention_type=item.intervention_type,
                peer_support=item.peer_support,
                weighted_success_score=item.weighted_success_score,
                weighted_similarity=item.weighted_similarity,
                evidence_score=item.evidence_score,
                historical_support=profile.sample_count if profile else 0,
                historical_confidence=profile.confidence if profile else None,
            )
        )

    return CrossMachineAnalysisResponse(
        machine_id=result.machine_id,
        recommendation=CrossMachineRecommendationResponse(
            target_machine_id=recommendation.target_machine_id,
            machine_type=recommendation.machine_type,
            evidence_scope=recommendation.evidence_scope.value,
            peer_count=recommendation.peer_count,
            interventions=interventions,
            recommended_intervention=recommendation.recommended_intervention,
            recommendation_confidence=recommendation.recommendation_confidence,
        ),
        evidence_note=result.evidence_note,
    )
