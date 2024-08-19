from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Any, List
from fastapi import APIRouter, FastAPI
from pydantic import TypeAdapter
from sqlalchemy import select

from .schema import HeroResponse, HeroSchema

from .settings import settings, AppSettings, get_settings
from .async_database import sessionmanager, SessionDep
from .models import HeroModel


print("this is an fastapi & sqlalchemy TEST!")


class App:

    def __init__(
        self,
        # lifespan: Callable,
        router: APIRouter | None,
        settings: AppSettings,
        init_db: bool,
    ):
        print(settings.DATABASE_URI)
        if init_db:
            sessionmanager.init(
                # "postgresql+asyncpg://admin:changethis@localhost:5432/async-asyncpg",
                settings.DATABASE_URI,
                settings.set_engine_args,
                settings.set_session_args,
            )

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            print("Welcome 🛬")
            print(f"Application v{app.version} started elegantly!")
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()
            get_settings.cache_clear()
            print(f"Application v{app.version} shut down gracefully!")

        self.__app = FastAPI(lifespan=lifespan, **settings.set_app_attributes)  # type: ignore
        self.__add_routes(router=router, settings=settings)

    def __add_routes(self, router: APIRouter | None, settings: AppSettings):
        if router:
            self.__app.include_router(router=router)

    def __call__(self) -> FastAPI:
        return self.__app


router = APIRouter(tags=["Hero"])


# Usage inside of a route
@router.post("/heroes", status_code=HTTPStatus.CREATED)
async def create_hero(session: SessionDep, hero_in: HeroSchema) -> HeroResponse:
    db_hero = await HeroModel.filterByName(session, hero_in.name)
    if db_hero:
        return HeroResponse(name=db_hero.name, source=db_hero.app_src, id=db_hero.id)
    hero = HeroModel(name=hero_in.name, app_src=hero_in.source)
    result = session.add(hero)
    await session.commit()
    return TypeAdapter(HeroResponse).validate_python(result)


@router.get("/heroes", status_code=HTTPStatus.OK)
async def get_hero(db: SessionDep) -> list[HeroResponse]:
    stmt = select(HeroModel).where(HeroModel.name.in_(["spongebob", "sandy"]))
    heroes = await db.execute(stmt)
    heroes_response = TypeAdapter(List[HeroResponse]).validate_python(heroes)
    return heroes_response


# Usage inside of a route using a db context
@router.get("/async_heroes")
async def db_context() -> Any:
    heroes = result = []
    async with sessionmanager.session() as session:
        async with session.begin():
            stmt = select(HeroModel).where()
            result = await session.scalars(stmt)
    for hero in result:
        print(hero)
        heroes.append(hero.name)
    return heroes


@router.post("/async_heroes")
async def create_context() -> Any:
    sandy = HeroModel(name="sandy")
    async with sessionmanager.session() as session:
        async with session.begin():
            result = session.add_all([sandy])
            await session.commit()
        return result


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "this is an fastapi-async-sqlalchemy TEST!"}


def initialize_application(init_db=True) -> FastAPI:
    return App(router=router, settings=settings, init_db=init_db)()


app = initialize_application()

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, lifespan="on")
