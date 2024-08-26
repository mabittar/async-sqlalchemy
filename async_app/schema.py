from uuid import UUID
from pydantic import BaseModel, Field


class HeroSchema(BaseModel):
    name: str
    source: str = Field(default="async_app")


class HeroResponse(HeroSchema):
    id: UUID

    class Config:
        from_attributes = True
