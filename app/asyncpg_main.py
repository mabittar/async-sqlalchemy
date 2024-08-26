# asyncpg
from fastapi import FastAPI
from .async_application import AsyncApp
from .async_router import async_router
from .settings import settings

db_url = "postgresql+asyncpg://admin:changethis@localhost:5432/load"


def initialize_application() -> FastAPI:
    return AsyncApp(
        router=async_router, settings=settings, db_url=db_url, init_db=True
    )()


app = initialize_application()

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, lifespan="on")
