from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "redpulse-ai",
    }


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    return {
        "status": "ready",
        "service": "redpulse-ai",
    }
