from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.event import EventStatus
from app.models.application import ApplicationStatus
from app.schemas.venue import VenueOut


class EventCreate(BaseModel):
    venue_id: int
    sport_type: str | None = None
    group_link: str | None = None
    scheduled_at: datetime | None = None
    price: float | None = None
    slots_total: int


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    captain_id: int
    venue: VenueOut
    sport_type: str | None
    group_link: str | None
    scheduled_at: datetime | None
    price: float | None
    slots_total: int
    slots_available: int
    status: EventStatus


class ApplicantOut(BaseModel):
    """Сжатое представление заявки, встраиваемое в детальный просмотр события.
    Не переиспользует ApplicationOut, чтобы не создавать циклический импорт
    между schemas/event.py и schemas/application.py."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ApplicationStatus
    user_id: int
    user_name: str

    @classmethod
    def from_application(cls, application) -> "ApplicantOut":
        return cls(
            id=application.id,
            status=application.status,
            user_id=application.user_id,
            user_name=application.user.name,
        )


class EventWithApplicants(EventOut):
    applicants: list[ApplicantOut] = []
