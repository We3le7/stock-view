from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置 - 从环境变量读取"""

    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "dev-secret-key"

    DATABASE_URL: str = "postgresql+asyncpg://stockview:stockview123@localhost:5432/stockview"

    REDIS_URL: str = "redis://localhost:6379/0"

    PRIMARY_DATA_SOURCE: str = "eastmoney"
    FALLBACK_DATA_SOURCE: str = "sina"

    AI_ADAPTER: str = "mock"
    AI_SERVICE_URL: str = "http://localhost:8001"
    AI_REQUEST_TIMEOUT: int = 30
    AI_CACHE_ENABLED: bool = True
    AI_CACHE_TTL: int = 300
    AI_RATE_LIMIT: int = 10

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    QUOTE_COLLECT_INTERVAL: int = 3
    QUOTE_CACHE_TTL: int = 5

    JWT_SECRET_KEY: str = "dev-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()