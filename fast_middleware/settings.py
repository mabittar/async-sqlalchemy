from enum import Enum
from functools import lru_cache
from os import environ
from pathlib import Path

from pydantic import (
    PostgresDsn,
    computed_field,
    field_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(str, Enum):
    LOCAL = "local"
    PRODUCTION = "production"


class AppSettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=f"{Path().resolve()}/.env",
        case_sensitive=True,
        validate_assignment=True,
        extra="allow",
    )
    TITLE: str = "Market Watch"
    VERSION: str = environ.get("APP_VERSION", "0.0.1")
    TIMEZONE: str = "UTC"
    DESCRIPTION: str = "Test "
    IS_DEBUG: bool = False
    DOCS_URL: str = environ.get("DOCS_URL", "/docs")
    OPENAPI_URL: str = environ.get("OPENAPI_URL", "/openapi.json")
    REDOC_URL: str = environ.get("REDOC_URL", "/redoc")
    ECHO_SQL: bool = bool(environ.get("ECHO_SQL", False))
    OPENAPI_PREFIX: str = ""

    HOST: str = environ.get("SERVER_HOST", "localhost")
    PORT: int = int(environ.get("SERVER_PORT", 8000))
    WORKERS: int = int(environ.get("SERVER_WORKERS", 1))

    POSTGRES_SERVER: str = str(environ.get("POSTGRES_SERVER"))
    POSTGRES_PORT: int = int(environ.get("POSTGRES_PORT", 5432))
    POSTGRES_POOL_SIZE: int = int(environ.get("POSTGRES_POOL_SIZE", 5))
    POSTGRES_USER: str = str(environ.get("POSTGRES_USER"))
    POSTGRES_PASSWORD: str = str(environ.get("POSTGRES_PASSWORD"))
    POSTGRES_DB: str = str(environ.get("POSTGRES_DB", "stock"))
    POSTGRES_ECHO: bool = bool(environ.get("POSTGRES_ECHO", False))
    DB: str | None = environ.get("DB", None)

    @property
    def DATABASE_URI(self) -> str:
        if self.DB is not None:
            return self.DB
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @classmethod
    @field_validator("DATABASE_URI")
    def check_db_name(cls, v):
        assert v.path and len(v.path) > 1, "database must be provided"
        return v

    @property  # type: ignore[prop-decorator]
    def set_app_attributes(self) -> dict[str, str | bool | None]:
        """
        Set all `FastAPI` class' attributes with the custom values defined in `BackendBaseSettings`.
        """
        return {
            "title": self.TITLE,
            "version": self.VERSION,
            "debug": self.IS_DEBUG,
            "description": self.DESCRIPTION,
            "docs_url": self.DOCS_URL,
            "openapi_url": self.OPENAPI_URL,
            "redoc_url": self.REDOC_URL,
            "openapi_prefix": self.OPENAPI_PREFIX,
            "echo_sql": self.ECHO_SQL,
        }


class AppLocalSettings(AppSettings):
    ENVIRONMENT: AppEnvironment = AppEnvironment.LOCAL
    DESCRIPTION: str = f"Application ({ENVIRONMENT})."


class AppProductionSettings(AppSettings):
    ENVIRONMENT: AppEnvironment = AppEnvironment.PRODUCTION
    DESCRIPTION: str = f"Application ({ENVIRONMENT})."


class FactoryAppSettings:
    def __init__(self, environment: str):
        self.environment = environment

    def __call__(self) -> AppSettings:
        if self.environment == AppEnvironment.PRODUCTION:
            return AppProductionSettings()
        return AppLocalSettings()


@lru_cache
def get_settings() -> AppSettings:
    return FactoryAppSettings(environment=environ.get("APP_ENV", "LOCAL"))()


settings = get_settings()
