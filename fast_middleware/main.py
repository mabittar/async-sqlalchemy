from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Any, Callable
from random import randrange
from uuid import uuid4
from uuid import UUID as UUIDClass
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from sqlalchemy import String, UUID, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware, db

from .settings import settings, AppSettings


print("this is an fastapi & sqlalchemy TEST!")
print(str(settings.DATABASE_URI))


engine_args = {  # engine arguments example
    "echo": True,  # print all SQL statements
    "pool_pre_ping": True,  # feature will normally emit SQL equivalent to “SELECT 1” each time a connection is checked out from the pool
    "pool_size": 5,  # number of connections to keep open at a time
    "max_overflow": 10,  # number of connections to allow to be opened above pool_size
}

session_args = {
    "expire_on_commit": False,  # False will prevent attributes from being expired
    "autoflush": False,
}

custom_engine = create_async_engine(str(settings.DATABASE_URI), **engine_args)

async_session = async_sessionmaker(
    bind=custom_engine, class_=AsyncSession, **session_args
)


# https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
class Base(DeclarativeBase):
    pass


class Hero(Base):
    __tablename__ = "heroes"

    id: Mapped[uuid4] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(30))
    app_src: Mapped[str] = mapped_column(default="middleware")

    def __repr__(self) -> str:
        return f"Hero(id={self.id!r}, name={self.name!r}"


class HeroDTO(BaseModel):
    id: UUIDClass
    name: str
    app_src: str

    class Config:
        from_attributes = True


@asynccontextmanager
async def lifespan(application: FastAPI):
    print("Welcome 🛬")
    print(f"Application v{application.version} started elegantly!")
    # outside of a request context cannot rely on ``SQLAlchemyMiddleware``
    # to create a database session
    # Usage outside of a route wirh db context
    async with db():
        result = await db.session.execute(select(Hero))
        for hero in result:
            print(hero)

    yield
    async with db():
        if db.session:
            print("Closing database connections")
            await db.session.close_all()
    print(f"Application v{application.version} shut down gracefully!")


class App:

    def __init__(
        self,
        lifespan: Callable,
        router: APIRouter | None,
        settings: AppSettings,
    ):
        self.__app = FastAPI(lifespan=lifespan, **settings.set_app_attributes)
        self.__add_routes(router=router)
        self.__app.add_middleware(
            SQLAlchemyMiddleware,
            commit_on_exit=True,
            custom_engine=custom_engine,
        )

    def __add_routes(self, router: APIRouter):
        if router:
            self.__app.include_router(router=router)

    def __call__(self) -> FastAPI:
        return self.__app


router = APIRouter(tags=["Heroes"])


# Usage inside of a route
@router.post("/heroes", status_code=HTTPStatus.CREATED)
async def create_hero() -> HeroDTO:
    random_hero = str(randrange(1, 50000))
    hero = Hero(name=random_hero)
    db.session.add_all([hero])
    await db.session.commit()
    await db.session.refresh(hero)
    return HeroDTO.model_validate(hero)


@router.get("/heroes", status_code=HTTPStatus.OK)
async def get_hero() -> list[HeroDTO]:
    heroes = await db.session.scalars(select(Hero))
    return [HeroDTO.model_validate(hero) for hero in heroes]


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "this is an fastapi-async-sqlalchemy TEST!"}


def initialize_application() -> FastAPI:
    return App(lifespan=lifespan, router=router, settings=settings)()


app = initialize_application()

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, lifespan="on")
