from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "telephony-service"
    app_env: str = "dev"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./telephony.db"
    core_backend_base_url: str = "http://localhost:8001"
    core_backend_timeout_seconds: float = 10.0

    default_caller_id: str | None = None


@lru_cache

def get_settings() -> Settings:
    return Settings()
