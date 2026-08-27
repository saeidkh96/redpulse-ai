import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.counterfactual_maintenance import router as counterfactual_maintenance_router
from app.api.v1.cross_machine import router as cross_machine_router
from app.api.v1.deviation import router as deviation_router
from app.api.v1.drift import router as drift_router
from app.api.v1.failures import router as failures_router
from app.api.v1.fleet_intelligence import router as fleet_intelligence_router
from app.api.v1.failure_matching import router as failure_matching_router
from app.api.v1.failure_prediction import router as failure_prediction_router
from app.api.v1.maintenance_recommendation import router as maintenance_recommendation_router
from app.api.v1.maintenance_verification import router as maintenance_verification_router
from app.api.v1.maintenance_history import router as maintenance_history_router
from app.api.v1.failure_explanation import router as failure_explanation_router
from app.api.v1.health import router as health_router
from app.api.v1.machine_dna import router as machine_dna_router
from app.api.v1.plant_intelligence import router as plant_intelligence_router
from app.api.v1.machine_health import router as machine_health_router
from app.api.v1.machines import router as machines_router
from app.api.v1.memory import router as memory_router
from app.api.v1.telemetry import router as telemetry_router
from app.core.config import get_settings
from app.core.database import close_database_connections
from app.core.logging import configure_logging
from app.core.redis import close_redis_connection


settings = get_settings()
configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info(
        "Starting %s v%s",
        settings.app_name,
        settings.app_version,
    )

    yield

    logger.info(
        "Stopping %s",
        settings.app_name,
    )

    await close_database_connections()
    await close_redis_connection()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)


app.include_router(
    health_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    machines_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    telemetry_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    machine_dna_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    deviation_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    drift_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    memory_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    machine_health_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    failures_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    failure_matching_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    failure_prediction_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    failure_explanation_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    maintenance_recommendation_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    maintenance_verification_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    maintenance_history_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    counterfactual_maintenance_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    cross_machine_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    fleet_intelligence_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    plant_intelligence_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }













