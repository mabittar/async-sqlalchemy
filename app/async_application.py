from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI
from .shared.async_database import asyncsessionmanager
from .settings import AppSettings, get_settings


class AsyncApp:

    def __init__(
        self,
        # lifespan: Callable,
        router: APIRouter | None,
        settings: AppSettings,
        db_url: str,
        init_db: bool,
    ):
        if init_db:
            db_str = settings.DATABASE_URI if settings.DATABASE_URI != '' else db_url
            asyncsessionmanager.init(
                db_str,
                settings.set_engine_args,
                settings.set_session_args,
            )

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            print("Welcome 🛬")
            print(f"Application v{app.version} started elegantly!")
            yield
            if asyncsessionmanager._engine is not None:
                await asyncsessionmanager.close()
            get_settings.cache_clear()
            print(f"Application v{app.version} shut down gracefully!")

        self.__app = FastAPI(lifespan=lifespan, **settings.set_app_attributes)  # type: ignore
        self.__add_routes(router=router)

    def __add_routes(self, router: APIRouter | None):
        if router:
            self.__app.include_router(router=router)

    def __call__(self) -> FastAPI:
        return self.__app
