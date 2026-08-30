from pydantic import BaseModel, Field


class RaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=300)
    speed: int = Field(ge=0)
