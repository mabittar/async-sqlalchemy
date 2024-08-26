from enum import Enum
from functools import lru_cache
from os import environ
from pathlib import Path
from typing import Literal
from typing_extensions import Self


from pydantic import (
    ValidationError,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.pool import QueuePool, NullPool


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

    TITLE: str = "Async Tests"
    VERSION: str = environ.get("APP_VERSION", "0.0.1")
    TIMEZONE: str = "UTC"
    DESCRIPTION: str = "Test "
    IS_DEBUG: bool = False
    DOCS_URL: str = environ.get("DOCS_URL", "/docs")
    OPENAPI_URL: str = environ.get("OPENAPI_URL", "/openapi.json")
    REDOC_URL: str = environ.get("REDOC_URL", "/redoc")
    OPENAPI_PREFIX: str = ""

    HOST: str = environ.get("SERVER_HOST", "localhost")
    PORT: int = int(environ.get("SERVER_PORT", 8000))
    WORKERS: int = int(environ.get("SERVER_WORKERS", 1))

    ECHO_SQL: bool = bool(environ.get("ECHO_SQL", False))
    POSTGRES_SCHEME: str = str(environ.get("POSTGRES_SCHEME", "postgresql+psycopg"))
    POSTGRES_SERVER: str = str(environ.get("POSTGRES_SERVER"))
    POSTGRES_PORT: int = int(environ.get("POSTGRES_PORT", 5432))
    POSTGRES_USER: str = str(environ.get("POSTGRES_USER"))
    POSTGRES_PASSWORD: str = str(environ.get("POSTGRES_PASSWORD"))
    POSTGRES_DB: str = str(environ.get("POSTGRES_DB"))
    DB_POOL_SIZE: int = int(environ.get("POSTGRES_POOL_SIZE", 20))
    BD_MAX_CONNECTIONS: int = int(environ.get("BD_MAX_CONNECTIONS", 10))
    BD_POOL_PRE_PING: bool = bool(environ.get("BD_POOL_PRE_PING", True))
    BD_EXPIRES_ON_COMMIT: bool = bool(environ.get("BD_EXPIRES_ON_COMMIT", True))
    DB_AUTO_FLUSH: bool = bool(environ.get("DB_AUTO_FLUSH", False))
    DB: str | None = str(environ.get("DB")) or None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URI(self) -> str:
        if self.DB is not None:
            return self.DB.replace('','')
        return str(
            MultiHostUrl.build(
                scheme=self.POSTGRES_SCHEME,
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

    # https://docs.sqlalchemy.org/en/14/core/pooling.html#switching-pool-implementations
    @property
    def set_engine_args(self) -> dict:
        poolclass = NullPool if "sqlite" not in self.DATABASE_URI else QueuePool
        return {  # engine arguments example
            "echo": self.ECHO_SQL,  # print all SQL statements
            # "poolclass": poolclass,  # Poll implementaion
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

    @model_validator(mode="after")
    def _mandatory_fields(self) -> Self:
        if not self.DATABASE_URI:
            raise ValidationError
        return self


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
