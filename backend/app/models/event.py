import enum
from datetime import datetime

from sqlalchemy import String, Integer, Numeric, ForeignKey, DateTime, Boolean, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EventStatus(str, enum.Enum):
    open = "open"
    full = "full"
    cancelled = "cancelled"
    completed = "completed"


class Event(Base):
    """Публикация сбора, созданная капитаном."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    captain_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"))
    sport_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    group_link: Mapped[str | None] = mapped_column(String(300), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    slots_total: Mapped[int] = mapped_column(Integer)
    slots_available: Mapped[int] = mapped_column(Integer)
    status: Mapped[EventStatus] = mapped_column(
        SAEnum(EventStatus, name="event_status", create_type=False),
        default=EventStatus.open,
    )
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    captain: Mapped["User"] = relationship(back_populates="events")
    venue: Mapped["Venue"] = relationship()
    applications: Mapped[list["EventApplication"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
