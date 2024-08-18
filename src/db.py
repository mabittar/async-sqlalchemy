import uuid
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, select

table_name = "sync-psycopg2"

print(f"Remember to create table {table_name} first!!!!!!!!")

DB = f"postgresql+psycopg2://admin:changethis@localhost:5432/{table_name}"


engine = create_engine(
    DB,
    echo=True,
)
Session = sessionmaker(
    bind=engine,
)


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


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Table created!")
    with Session() as session:
        hero1 = Hero(name="spongebob")
        hero2 = Hero(name="sandy")
        session.add_all([hero1, hero2])
        session.commit()

    with Session() as session:
        for hero in session.scalars(select(Hero)):
            print(hero)
