from pydantic import BaseModel, Field


class HeroSchema(BaseModel):
    name: str
    source: str = Field(default="async_app")


class HeroResponse(HeroSchema):
    id: str

    class Config:
        orm_mode = True
