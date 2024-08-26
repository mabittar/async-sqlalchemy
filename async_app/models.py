import uuid
from datetime import datetime
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, class_mapper
from sqlalchemy import UUID


# https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
class Base(DeclarativeBase):
    pass


class HeroModel(Base):
    __tablename__ = "heroes"

    id: Mapped[uuid.uuid4] = mapped_column(  # type: ignore
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(unique=True)
    app_src: Mapped[str] = mapped_column(default="async_app")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"Hero(id={self.id!r}, name={self.name!r}"

    def model_to_dict(cls) -> dict:
        return {c.key: getattr(cls, c.key) for c in class_mapper(cls.__class__).columns}

    @classmethod
    async def get_all(cls, db: AsyncSession):
        return (await db.execute(select(cls))).scalars().all()

    @classmethod
    async def create(cls, db: AsyncSession, id=None, **kwargs):
        if not id:
            id = uuid.uuid4().hex
        app_src = kwargs["source"]
        transaction = cls(id=id, name=kwargs["name"], app_src=app_src)
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction

    @classmethod
    async def get(cls, db: AsyncSession, id: str):
        try:
            transaction = await db.get(cls, id)
        except NoResultFound:
            return None
        return transaction

    @classmethod
    async def filterByName(cls, db: AsyncSession, name: str):
        stmt = select(HeroModel).where(HeroModel.name == name)
        result = await db.execute(stmt)
        transaction = result.scalar_one_or_none()
        return transaction

    @classmethod
    async def filterBySource(cls, db: AsyncSession, source: str):
        stmt = select(HeroModel).where(HeroModel.app_src == source)
        try:
            result = await db.execute(stmt)
            transactions = result.scalars().all()
        except NoResultFound:
            return None
        return transactions
