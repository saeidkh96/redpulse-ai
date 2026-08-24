import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    yield
    logger.info("Stopping %s", settings.app_name)


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


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }
