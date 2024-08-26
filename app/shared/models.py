import uuid
from datetime import datetime
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy import UUID, Column, DateTime, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Base(DeclarativeBase):

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


# One user can have many toys as toys can have many users
# Example of Many-to-many relantionship, everything else will be simlpe than this.

user_toy_association = Table(
    "user_toy",
    Base.metadata,
    Column("users_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("toys_id", UUID(as_uuid=True), ForeignKey("toys.id")),
)


class ToyModel(Base):
    __tablename__ = "toys"

    id: Mapped[uuid.uuid4] = mapped_column(  # type: ignore
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    name: Mapped[str] = mapped_column(nullable=False)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.uuid4] = mapped_column(  # type: ignore
        UUID(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(nullable=False)
    toys: Mapped[list["ToyModel"]] = relationship(
        secondary=user_toy_association, backref="users", lazy="selectin"
    )
