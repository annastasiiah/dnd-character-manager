from pydantic import BaseModel, ConfigDict, Field


class CharacterBackgroundResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class CharacterBackgroundCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class CharacterBackgroundUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
