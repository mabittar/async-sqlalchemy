from http import HTTPStatus
from uuid import UUID
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from .shared.schema import ToyRequest, ToyDTO, UserRequest, UserDTO
from .shared.models import ToyModel, UserModel
from .shared.database import SessionDep

router = APIRouter(tags=["Router"])


@router.post("/toys", status_code=HTTPStatus.CREATED)
async def create_toy(session: SessionDep, input: ToyRequest) -> ToyDTO:
    result = session.scalars(select(ToyModel).where(ToyModel.name == input.name))
    existing_toy = result.one_or_none()
    if existing_toy:
        return ToyDTO.model_validate(existing_toy)
    toy = ToyModel(**input.model_dump())
    session.add(toy)
    session.commit()
    session.refresh(toy)
    return ToyDTO.model_validate(toy)


@router.get("/toys", status_code=HTTPStatus.OK)
async def get_all_toys(session: SessionDep) -> list[ToyDTO]:
    result = session.scalars(select(ToyModel))
    toys = result.all()
    return [ToyDTO.model_validate(toy) for toy in toys]


@router.get("/toys/{id}", status_code=HTTPStatus.OK)
async def get_toy_by_id(id: UUID, session: SessionDep) -> ToyDTO:
    toy = session.get(ToyModel, id)
    if not toy:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"can not find if toy with id: {id}"
        )
    return ToyDTO.model_validate(toy)


@router.post("/users", status_code=HTTPStatus.CREATED)
async def create_user(session: SessionDep, input: UserRequest) -> UserDTO:
    data = input.model_dump()
    ids = data.pop("toys")
    result = session.scalars(select(ToyModel).where(ToyModel.id.in_(ids)))
    toys = result.all()
    if not len(toys):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"can not find if toy with ids: {ids}",
        )
    user = UserModel(**data, toys=toys)
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserDTO.model_validate(user)


@router.get("/users", status_code=HTTPStatus.OK)
async def get_all_users(session: SessionDep) -> list[UserDTO]:
    result = session.scalars(select(UserModel))
    users = result.all()
    return [UserDTO.model_validate(user) for user in users]


@router.get("/users/{id}", status_code=HTTPStatus.OK)
async def get_user_by_id(id: UUID, session: SessionDep) -> UserDTO:
    user = session.get(UserModel, id)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"can not find user with id: {id}"
        )
    return UserDTO.model_validate(user)
