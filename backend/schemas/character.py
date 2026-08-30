from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class CharacterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    race_id: int
    level: int = Field(ge=1, le=20)

    strength: int = Field(ge=1, le=30)
    dexterity: int = Field(ge=1, le=30)
    constitution: int = Field(ge=1, le=30)
    intelligence: int = Field(ge=1, le=30)
    wisdom: int = Field(ge=1, le=30)
    charisma: int = Field(ge=1, le=30)

class CharacterResponse(BaseModel):
    id: int
    name: str
    race_id: int
    level: int

    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CharacterUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    race_id: int | None = None
    level: int | None = Field(None, ge=1, le=20)

    strength: int | None = Field(None, ge=1, le=30)
    dexterity: int | None = Field(None, ge=1, le=30)
    constitution: int | None = Field(None, ge=1, le=30)
    intelligence: int | None = Field(None, ge=1, le=30)
    wisdom: int | None = Field(None, ge=1, le=30)
    charisma: int | None = Field(None, ge=1, le=30)