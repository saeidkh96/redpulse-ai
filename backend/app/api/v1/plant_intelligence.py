from fastapi import APIRouter, HTTPException

from app.plant.early_warning import (
    FleetEarlyWarningInput,
    fleet_early_warning_engine,
)
from app.plant.maintenance import (
    PlantMaintenanceInput,
    plant_maintenance_engine,
)
from app.plant.risk_forecasting import (
    FleetRiskObservation,
    fleet_risk_forecasting_engine,
)
from app.plant.site_intelligence import (
    PlantFleetInput,
    plant_intelligence_engine,
)
from app.schemas.plant_intelligence import (
    FleetEarlyWarningRequest,
    FleetRiskForecastRequest,
    PlantIntelligenceRequest,
    PlantMaintenanceRequest,
)


router = APIRouter(prefix="/plant", tags=["plant-intelligence"])


@router.post("/sites/summary")
async def plant_summary(payload: PlantIntelligenceRequest) -> dict:
    result = plant_intelligence_engine.summarize(
        [PlantFleetInput(**item.model_dump()) for item in payload.fleets]
    )
    return {
        "sites": [
            {
                **{
                    key: value
                    for key, value in item.__dict__.items()
                    if key != "fleets"
                },
                "fleets": [fleet.__dict__ for fleet in item.fleets],
            }
            for item in result
        ]
    }


@router.post("/fleet-early-warning")
async def fleet_early_warning(payload: FleetEarlyWarningRequest) -> dict:
    signals = [
        fleet_early_warning_engine.analyze(
            FleetEarlyWarningInput(**item.model_dump())
        )
        for item in payload.fleets
    ]
    signals.sort(key=lambda item: item.warning_score, reverse=True)
    return {"warnings": [item.__dict__ for item in signals]}


@router.post("/fleet-risk-forecast")
async def fleet_risk_forecast(payload: FleetRiskForecastRequest) -> dict:
    try:
        result = fleet_risk_forecasting_engine.forecast(
            [
                FleetRiskObservation(**item.model_dump())
                for item in payload.observations
            ],
            horizon_steps=payload.horizon_steps,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result.__dict__


@router.post("/maintenance-plan")
async def plant_maintenance_plan(payload: PlantMaintenanceRequest) -> dict:
    result = plant_maintenance_engine.plan(
        [
            PlantMaintenanceInput(**item.model_dump())
            for item in payload.items
        ],
        capacity_by_site=payload.capacity_by_site,
    )
    return {
        "sites": [
            {
                "site_id": plan.site_id,
                "selected_actions": [
                    action.__dict__
                    for action in plan.selected_actions
                ],
                "deferred_machine_ids": plan.deferred_machine_ids,
                "used_capacity_units": plan.used_capacity_units,
                "total_capacity_units": plan.total_capacity_units,
            }
            for plan in result
        ]
    }
