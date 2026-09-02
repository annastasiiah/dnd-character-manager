from pydantic import BaseModel, ConfigDict


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