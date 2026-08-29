from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user import User
    from models.race import Race

class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
        )
    race_id: Mapped[int] = mapped_column(
        ForeignKey("races.id"),
        nullable=False
        )
    name: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
        )
    level: Mapped[int] = mapped_column(nullable=False)
    strength: Mapped[int] = mapped_column(nullable=False)
    dexterity: Mapped[int] = mapped_column(nullable=False)
    constitution: Mapped[int] = mapped_column(nullable=False)
    intelligence: Mapped[int] = mapped_column(nullable=False)
    wisdom: Mapped[int] = mapped_column(nullable=False)
    charisma: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
        )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="characters"
        )

    race: Mapped["Race"] = relationship(
        "Race",
        back_populates="characters"
    )
