from fastapi import APIRouter, HTTPException

from app.data_platform.contracts import AnalyticsJob
from app.data_platform.orchestrator import DataPlatformOrchestrator
from app.schemas.data_platform import AnalyticsJobRequest, StreamingEventPayload
from app.streaming.bus import InMemoryEventBus

router = APIRouter(prefix="/data-platform", tags=["data-platform"])
event_bus = InMemoryEventBus()
orchestrator = DataPlatformOrchestrator()

@router.post("/events/publish")
async def publish_event(payload: StreamingEventPayload) -> dict:
    event_bus.publish(payload.topic, payload.event)
    return {"status": "published", "topic": payload.topic}

@router.get("/events/recent")
async def recent_events(limit: int = 100) -> dict:
    limit = max(1, min(limit, 1000))
    return {
        "events": [
            {"topic": topic, "event": event}
            for topic, event in event_bus.published[-limit:]
        ]
    }

@router.post("/analytics/run")
async def run_analytics(payload: AnalyticsJobRequest) -> dict:
    try:
        result = orchestrator.execute(
            AnalyticsJob(
                name=payload.name,
                input_path=payload.input_path,
                output_path=payload.output_path,
                engine=payload.engine,
            )
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "job_name": result.job_name,
        "status": result.status,
        "output_path": result.output_path,
        "metadata": result.metadata,
    }
