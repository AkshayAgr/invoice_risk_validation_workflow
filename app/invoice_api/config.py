from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    foundry_agent_endpoint: str = ""
    foundry_api_version: str = "2025-11-15-preview"
    foundry_timeout_seconds: float = Field(default=120, ge=5, le=600)
    foundry_max_retries: int = Field(default=3, ge=0, le=6)
    max_concurrent_foundry_calls: int = Field(default=20, ge=1, le=100)
    queue_timeout_seconds: float = Field(default=10, ge=1, le=60)
    max_request_bytes: int = Field(default=16_384, ge=1024, le=1_048_576)
    auth_mode: str = "entra"
    allowed_origins: str = ""
    log_level: str = "INFO"

    @field_validator("foundry_agent_endpoint")
    @classmethod
    def normalize_endpoint(cls, value: str) -> str:
        return value.rstrip("/")

    @field_validator("auth_mode")
    @classmethod
    def validate_auth_mode(cls, value: str) -> str:
        value = value.lower()
        if value not in {"entra", "disabled"}:
            raise ValueError("AUTH_MODE must be 'entra' or 'disabled'")
        return value

    @property
    def origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
