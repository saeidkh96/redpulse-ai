from fastapi import APIRouter, Response, status

from app.core.database import check_database_connection
from app.core.redis import check_redis_connection


router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "redpulse-ai",
    }


@router.get("/ready")
async def readiness_check(response: Response) -> dict[str, object]:
    database_ready = await check_database_connection()
    redis_ready = await check_redis_connection()

    ready = database_ready and redis_ready

    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if ready else "not_ready",
        "service": "redpulse-ai",
        "dependencies": {
            "database": "up" if database_ready else "down",
            "redis": "up" if redis_ready else "down",
        },
    }
