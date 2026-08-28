from fastapi import APIRouter, HTTPException

from app.schemas.mlops_platform import (
    ControlPlaneRequest,
    ExperimentRunRequest,
    FeatureWriteRequest,
    PromotionRequest,
    RegisterModelRequest,
)
from app.services.mlops_platform import MLOpsPlatformService


router = APIRouter(prefix="/mlops", tags=["mlops"])
service = MLOpsPlatformService()


@router.post("/models")
async def register_model(payload: RegisterModelRequest) -> dict:
    try:
        model = service.register_model(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return model.__dict__


@router.get("/models/{model_name}")
async def list_models(model_name: str) -> dict:
    return {"models": [item.__dict__ for item in service.registry.list_versions(model_name)]}


@router.post("/experiments")
async def log_experiment(payload: ExperimentRunRequest) -> dict:
    run = service.log_experiment(**payload.model_dump())
    return run.__dict__


@router.post("/control-plane/assess")
async def assess_control_plane(payload: ControlPlaneRequest) -> dict:
    try:
        result = service.control_plane.assess(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result.__dict__


@router.post("/models/promote")
async def promote_model(payload: PromotionRequest) -> dict:
    try:
        result = service.lifecycle.promote_to_champion(
            payload.model_name,
            payload.version,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result.__dict__


@router.post("/features")
async def write_features(payload: FeatureWriteRequest) -> dict:
    service.feature_store.put(
        payload.entity_id,
        payload.feature_group,
        payload.features,
    )
    return {"status": "stored"}


@router.get("/features/{entity_id}/{feature_group}")
async def read_features(entity_id: str, feature_group: str) -> dict:
    try:
        return service.feature_store.get(entity_id, feature_group)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
