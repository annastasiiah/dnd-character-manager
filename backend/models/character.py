from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.background import CharacterBackground
    from models.character_class import CharacterClass
    from models.race import Race
    from models.spell import Spell
    from models.user import User

class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), nullable=False)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), nullable=False)
    background_id: Mapped[int] = mapped_column(ForeignKey("backgrounds.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[int] = mapped_column(nullable=False)
    strength: Mapped[int] = mapped_column(nullable=False)
    dexterity: Mapped[int] = mapped_column(nullable=False)
    constitution: Mapped[int] = mapped_column(nullable=False)
    intelligence: Mapped[int] = mapped_column(nullable=False)
    wisdom: Mapped[int] = mapped_column(nullable=False)
    charisma: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    user: Mapped["User"] = relationship("User", back_populates="characters")

    race: Mapped["Race"] = relationship("Race", back_populates="characters")

    character_class: Mapped["CharacterClass"] = relationship(
        "CharacterClass",
        back_populates="characters",
    )

    background: Mapped["CharacterBackground"] = relationship(
        "CharacterBackground",
        back_populates="characters",
    )

    spells: Mapped[list["Spell"]] = relationship(
        "Spell",
        secondary="character_spells",
        back_populates="characters",
    )

