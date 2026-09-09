from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.background import CharacterBackgroundResponse
from schemas.character_class import CharacterClassResponse
from schemas.race import RaceResponse


class CharacterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    race_id: int
    level: int = Field(ge=1, le=20)
    class_id: int
    background_id: int

    strength: int = Field(ge=1, le=30)
    dexterity: int = Field(ge=1, le=30)
    constitution: int = Field(ge=1, le=30)
    intelligence: int = Field(ge=1, le=30)
    wisdom: int = Field(ge=1, le=30)
    charisma: int = Field(ge=1, le=30)


class CharacterResponse(BaseModel):
    id: int
    name: str
    level: int

    # The raw ids stay in the payload so an edit form can round-trip them,
    # and the expanded objects save the client three lookups per character.
    race_id: int
    class_id: int
    background_id: int

    race: RaceResponse
    character_class: CharacterClassResponse
    background: CharacterBackgroundResponse

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
    class_id: int | None = None
    background_id: int | None = None
    level: int | None = Field(None, ge=1, le=20)

    strength: int | None = Field(None, ge=1, le=30)
    dexterity: int | None = Field(None, ge=1, le=30)
    constitution: int | None = Field(None, ge=1, le=30)
    intelligence: int | None = Field(None, ge=1, le=30)
    wisdom: int | None = Field(None, ge=1, le=30)
    charisma: int | None = Field(None, ge=1, le=30)
