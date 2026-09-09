from pydantic import BaseModel, ConfigDict, Field


class SpellResponse(BaseModel):
    id: int
    name: str
    level: int
    school: str
    casting_time: str
    spell_range: str
    duration: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class SpellListResponse(BaseModel):
    """A page of spells plus the total, so the client can render a pager."""

    items: list[SpellResponse]
    total: int
    limit: int
    offset: int


class CharacterSpellCreate(BaseModel):
    spell_id: int


class SpellCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    level: int = Field(ge=0, le=9)
    school: str = Field(min_length=1, max_length=50)
    casting_time: str = Field(min_length=1, max_length=50)
    spell_range: str = Field(min_length=1, max_length=50)
    duration: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1)


class SpellUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    level: int | None = Field(None, ge=0, le=9)
    school: str | None = Field(None, min_length=1, max_length=50)
    casting_time: str | None = Field(None, min_length=1, max_length=50)
    spell_range: str | None = Field(None, min_length=1, max_length=50)
    duration: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, min_length=1)
