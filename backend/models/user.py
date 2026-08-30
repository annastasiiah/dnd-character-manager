from datetime import datetime, timezone

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.character import Character

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
        )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
        )
    role: Mapped[str] = mapped_column(
        String(20), 
        default="user",
        nullable=False
        )
    nickname: Mapped[str] = mapped_column(
        String(50), 
        unique=True,
        nullable=False
        )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
        )
    characters: Mapped[list["Character"]] = relationship(
        "Character",
        back_populates="user",
        cascade="all, delete-orphan"
    )
