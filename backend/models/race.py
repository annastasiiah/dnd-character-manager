from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.character import Character

class Race(Base):
    __tablename__ = "races"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50),nullable=False)
    description: Mapped[str] = mapped_column(String(300),nullable=False)
    speed: Mapped[int] = mapped_column(nullable=False)

    characters: Mapped[list["Character"]] = relationship(
        "Character",
        back_populates="race"
    )