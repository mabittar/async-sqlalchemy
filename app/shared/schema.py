from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class ToyRequest(BaseModel):
    name: str = Field(description="create toy", min_length=1, max_length=50)


class ToyDTO(ToyRequest):
    id: UUID

    class Config:
        from_attributes = True


class UserRequest(BaseModel):
    name: Optional[str] = Field(
        description="insert user name or will be create randomly"
    )
    toys: list[UUID] = Field(min_length=1, description="list all toys to be associated to this user")


class UserDTO(BaseModel):
    id: UUID
    name: str
    toys: list[ToyDTO]

    class Config:
        from_attributes = True

class AssociateUserToysRequest(BaseModel):
    user_id: UUID
    toys: list[UUID] = Field(min_length=1)
