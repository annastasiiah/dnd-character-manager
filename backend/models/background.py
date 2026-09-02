from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.character import Character


class CharacterBackground(Base):
    __tablename__ = "backgrounds"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    characters: Mapped[list["Character"]] = relationship(
        "Character",
        back_populates="background",
    )