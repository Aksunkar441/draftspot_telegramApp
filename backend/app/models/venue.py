import enum

from sqlalchemy import String, Numeric, Boolean, Enum as SAEnum, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VenueStatus(str, enum.Enum):
    free = "free"
    occupied = "occupied"


class Venue(Base):
    """
    Площадка/корт. Список таких объектов готовится платформой заранее
    (геоданные + платность). Дворовые площадки всегда is_paid=False и
    статус occupied/free для них не применяется (используется только
    для платных кортов с реальным расписанием).
    """

    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    sport_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[VenueStatus] = mapped_column(SAEnum(VenueStatus), default=VenueStatus.free)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
