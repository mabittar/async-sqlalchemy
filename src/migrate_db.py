import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, select

table_name = "migrate"

print(f"use: alembic init -t async alembic")
print(f"after edit alembic/env.py to reflect config")
print(f"use alembic revision --autogenerate")
print(f"then: alembic upgrade head")

MIGRATE_DB = f"postgresql+asyncpg://admin:changethis@localhost:5432/{table_name}"


async_engine = create_async_engine(
    MIGRATE_DB,
    echo=True,
    future=True,
)


@asynccontextmanager
async def get_conn():
    async with async_engine.begin() as connection:
        try:
            yield connection
        except Exception:
            await connection.rollback()
            raise


@asynccontextmanager
async def get_session():
    try:
        async_session = async_sessionmaker(async_engine, class_=AsyncSession)

        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


class Base(DeclarativeBase):
    pass


class Hero(Base):
    __tablename__ = "heroes"

    id: Mapped[uuid.uuid4] = mapped_column(  # type: ignore
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"Hero(id={self.id!r}, name={self.name!r}"


def create_all():
    print("use alembic migrations to create tables!")


async def main():
    create_all()
    async with get_session() as session:
        hero1 = Hero(name="spongebob")
        hero2 = Hero(name="sandy")
        session.add_all([hero1, hero2])
        await session.commit()

    async with get_session() as session:
        for hero in await session.scalars(select(Hero)):
            print(hero)


if __name__ == "__main__":
    asyncio.run(main())
