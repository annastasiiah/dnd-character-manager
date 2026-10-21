
from pydantic import BaseModel, ConfigDict, Field


class CharacterClassResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    primary_ability: str | None = None
    hit_die: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CharacterClassCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str | None = None
    primary_ability: str | None = Field(None, max_length=100)
    hit_die: str | None = Field(None, max_length=10)


class CharacterClassUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = None
    primary_ability: str | None = Field(None, max_length=100)
    hit_die: str | None = Field(None, max_length=10)
