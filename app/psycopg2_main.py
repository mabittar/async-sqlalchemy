# asyncpg
from fastapi import FastAPI
from .application import Application
from .router import router
from .settings import settings

db_url = "postgresql+psycopg2://admin:changethis@localhost:5432/load"


def initialize_application() -> FastAPI:
    return Application(
        router=router, settings=settings, db_url=settings.DATABASE_URI, init_db=True
    )()


app = initialize_application()

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, lifespan="on")
