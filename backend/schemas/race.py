from pydantic import BaseModel, ConfigDict, Field


class RaceResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class RaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=100)
    speed: int = Field(ge=1)