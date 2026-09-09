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

class CharacterSpellCreate(BaseModel):
    spell_id: int

class SpellCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    level: int = Field(ge=0)
    school: str = Field(min_length=1, max_length=50)
    casting_time: str = Field(min_length=1, max_length=50)
    spell_range: str = Field(min_length=1, max_length=50)
    duration: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1)
