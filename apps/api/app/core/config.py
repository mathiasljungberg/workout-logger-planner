from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_csv(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        return value
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str = "change-me"
    session_cookie_name: str = "workout_tracker_session"
    admin_username: str = "admin"
    admin_password: str = "admin"
    database_url: str = "sqlite:///./app.db"
    frontend_dist_dir: str = "app/static"
    cors_origins: Annotated[list[str], BeforeValidator(_parse_csv)] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
