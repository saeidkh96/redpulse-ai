from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RedPulse AI"
    app_version: str = "4.0.0"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://redpulse:redpulse@localhost:5433/redpulse"
    redis_url: str = "redis://localhost:6379/0"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "redpulse-v40-intelligence"
    telemetry_topic: str = "redpulse.telemetry.v1"
    integration_max_attempts: int = 3
    api_rate_limit_per_minute: int = 120
    otel_service_name: str = "redpulse-ai"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
