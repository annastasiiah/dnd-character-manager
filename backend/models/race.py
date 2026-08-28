from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Race(Base):
    __tablename__ = "races"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(300))
    speed: Mapped[int]