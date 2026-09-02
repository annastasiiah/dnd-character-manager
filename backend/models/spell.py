from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.character import Character


class Spell(Base):
    __tablename__ = "spells"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    level: Mapped[int] = mapped_column(nullable=False)
    school: Mapped[str] = mapped_column(String(50), nullable=False)
    casting_time: Mapped[str] = mapped_column(String(50), nullable=False)
    spell_range: Mapped[str] = mapped_column(String(50), nullable=False)
    duration: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    characters: Mapped[list["Character"]] = relationship(
        "Character",
        secondary="character_spells",
        back_populates="spells",
    )
