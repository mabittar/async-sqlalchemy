from enum import Enum
from functools import lru_cache
from os import environ
from pathlib import Path

from pydantic import (
    computed_field,
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
    DB_POOL_SIZE: int = int(environ.get("POSTGRES_POOL_SIZE", 5))
    BD_MAX_CONNECTIONS: int = int(environ.get("BD_MAX_CONNECTIONS", 10))
    POSTGRES_USER: str = str(environ.get("POSTGRES_USER"))
    POSTGRES_PASSWORD: str = str(environ.get("POSTGRES_PASSWORD"))
    POSTGRES_DB: str = str(environ.get("POSTGRES_DB"))
    DB_ECHO: bool = bool(environ.get("DB_ECHO", False))
    BD_POOL_PRE_PING: bool = bool(environ.get("BD_POOL_PRE_PING", True))
    BD_EXPIRES_ON_COMMIT: bool = bool(environ.get("BD_EXPIRES_ON_COMMIT", True))
    DB_AUTO_FLUSH: bool = bool(environ.get("DB_AUTO_FLUSH", False))
    DB: str | None = environ.get("DB", None)

    @property
    def DATABASE_URI(self) -> str:
        if self.DB is not None:
            return self.DB
        return str(
            MultiHostUrl.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

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

    @property
    def set_engine_args(self) -> dict:
        return {  # engine arguments example
            "echo": self.DB_ECHO,  # print all SQL statements
            "pool_pre_ping": self.BD_POOL_PRE_PING,  # feature will normally emit SQL equivalent to “SELECT 1” each time a connection is checked out from the pool
            "pool_size": self.DB_POOL_SIZE,  # number of connections to keep open at a time
            "max_overflow": self.BD_MAX_CONNECTIONS,  # number of connections to allow to be opened above pool_size
        }

    @property
    def set_session_args(self) -> dict:
        return {
            "expire_on_commit": self.BD_EXPIRES_ON_COMMIT,  # False will prevent attributes from being expired
            "autoflush": self.DB_AUTO_FLUSH,
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
    app_env = environ.get("APP_ENV", "LOCAL")
    return FactoryAppSettings(environment=app_env.upper())()


settings = get_settings()
