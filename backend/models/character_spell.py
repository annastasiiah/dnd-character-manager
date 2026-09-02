from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class CharacterSpell(Base):
    __tablename__ = "character_spells"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"),
        primary_key=True,
    )

    spell_id: Mapped[int] = mapped_column(
        ForeignKey("spells.id"),
        primary_key=True,
    )