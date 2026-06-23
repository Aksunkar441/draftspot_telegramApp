from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EventFavorite(Base):
    """Сохраненное пользователем событие из ленты."""

    __tablename__ = "event_favorites"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_favorite_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    event: Mapped["Event"] = relationship(back_populates="favorites")
    user: Mapped["User"] = relationship(back_populates="favorites")
