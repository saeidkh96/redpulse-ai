from redis.asyncio import Redis

from app.core.config import get_settings


settings = get_settings()

redis_client = Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


async def check_redis_connection() -> bool:
    try:
        return bool(await redis_client.ping())
    except Exception:
        return False


async def close_redis_connection() -> None:
    await redis_client.aclose()
