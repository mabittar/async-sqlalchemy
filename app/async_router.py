from http import HTTPStatus
from uuid import UUID
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from .shared.schema import ToyRequest, ToyDTO, UserRequest, UserDTO
from .shared.models import ToyModel, UserModel
from .shared.async_database import AsyncSessionDep

async_router = APIRouter(tags=["Async Router"])


@async_router.post("/toys", status_code=HTTPStatus.CREATED)
async def create_toy(session: AsyncSessionDep, input: ToyRequest) -> ToyDTO:
    result = await session.scalars(select(ToyModel).where(ToyModel.name == input.name))
    existing_toy = result.one_or_none()
    if existing_toy:
        return ToyDTO.model_validate(existing_toy)
    toy = ToyModel(**input.model_dump())
    session.add(toy)
    await session.commit()
    await session.refresh(toy)
    return ToyDTO.model_validate(toy)


@async_router.get("/toys", status_code=HTTPStatus.OK)
async def get_all_toys(session: AsyncSessionDep) -> list[ToyDTO]:
    result = await session.scalars(select(ToyModel))
    toys = result.all()
    return [ToyDTO.model_validate(toy) for toy in toys]


@async_router.get("/toys/{id}", status_code=HTTPStatus.OK)
async def get_toy_by_id(id: UUID, session: AsyncSessionDep) -> ToyDTO:
    toy = await session.get(ToyModel, id)
    if not toy:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"can not find if toy with id: {id}",
        )
    return ToyDTO.model_validate(toy)


@async_router.post("/users", status_code=HTTPStatus.CREATED)
async def create_user(session: AsyncSessionDep, input: UserRequest) -> UserDTO:
    data = input.model_dump()
    ids = data.pop("toys")
    result = await session.scalars(select(ToyModel).where(ToyModel.id.in_(ids)))
    toys = result.all()
    if not len(toys):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"can not find if toy with ids: {ids}",
        )
    user = UserModel(**data, toys=toys)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserDTO.model_validate(user)


@async_router.get("/users", status_code=HTTPStatus.OK)
async def get_all_users(session: AsyncSessionDep) -> list[UserDTO]:
    result = await session.scalars(select(UserModel))
    users = result.all()
    return [UserDTO.model_validate(user) for user in users]


@async_router.get("/users/{id}", status_code=HTTPStatus.OK)
async def get_user_by_id(id: UUID, session: AsyncSessionDep) -> UserDTO:
    user = await session.get(UserModel, id)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"can not find user with id: {id}"
        )
    return UserDTO.model_validate(user)
