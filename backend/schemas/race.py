from pydantic import BaseModel, ConfigDict, Field


class RaceResponse(BaseModel):
    id: int
    name: str
    description: str
    speed: int

    model_config = ConfigDict(from_attributes=True)


class RaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=300)
    speed: int = Field(ge=1)


class RaceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, min_length=1, max_length=300)
    speed: int | None = Field(None, ge=1)
