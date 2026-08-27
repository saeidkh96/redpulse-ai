from fastapi import APIRouter

from app.fleet.health import MachineFleetState, fleet_health_engine
from app.fleet.hotspots import FleetFailureEvidence, fleet_failure_hotspot_engine
from app.fleet.peer_groups import peer_group_engine
from app.fleet.prioritization import (
    MaintenancePriorityInput,
    fleet_maintenance_prioritization_engine,
)
from app.fleet.similarity import MachineBehaviorProfile
from app.schemas.fleet_intelligence import (
    FleetHealthRequest,
    FleetHotspotRequest,
    FleetPrioritizationRequest,
    PeerGroupRequest,
)


router = APIRouter(prefix="/fleet", tags=["fleet-intelligence"])


@router.post("/peer-groups")
async def build_peer_group(payload: PeerGroupRequest) -> dict:
    target = MachineBehaviorProfile(**payload.target.model_dump())
    candidates = [
        MachineBehaviorProfile(**item.model_dump())
        for item in payload.candidates
    ]
    result = peer_group_engine.build(
        target,
        candidates,
        minimum_similarity=payload.minimum_similarity,
        limit=payload.limit,
    )
    return {
        "target_machine_id": result.target_machine_id,
        "minimum_similarity": result.minimum_similarity,
        "size": result.size,
        "peers": [item.__dict__ for item in result.peers],
    }


@router.post("/health")
async def fleet_health(payload: FleetHealthRequest) -> dict:
    result = fleet_health_engine.summarize(
        [MachineFleetState(**item.model_dump()) for item in payload.machines]
    )
    return {
        "machine_count": result.machine_count,
        "fleet_health_score": result.fleet_health_score,
        "fleet_risk_score": result.fleet_risk_score,
        "critical_machine_count": result.critical_machine_count,
        "degraded_machine_count": result.degraded_machine_count,
        "healthy_machine_count": result.healthy_machine_count,
        "machines": [item.__dict__ for item in result.machines],
    }


@router.post("/failure-hotspots")
async def failure_hotspots(payload: FleetHotspotRequest) -> dict:
    hotspots = fleet_failure_hotspot_engine.detect(
        [FleetFailureEvidence(**item.model_dump()) for item in payload.evidence],
        minimum_risk=payload.minimum_risk,
    )
    return {"hotspots": [item.__dict__ for item in hotspots]}


@router.post("/maintenance-priorities")
async def maintenance_priorities(payload: FleetPrioritizationRequest) -> dict:
    priorities = fleet_maintenance_prioritization_engine.prioritize(
        [MaintenancePriorityInput(**item.model_dump()) for item in payload.machines],
        capacity=payload.capacity,
    )
    return {"priorities": [item.__dict__ for item in priorities]}
