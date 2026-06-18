from datetime import datetime

from sqlalchemy import BigInteger, String, Integer, ARRAY, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    photos: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    city: Mapped[str] = mapped_column(String(100), default="Тараз")
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    events: Mapped[list["Event"]] = relationship(back_populates="captain")
    applications: Mapped[list["EventApplication"]] = relationship(back_populates="user")
