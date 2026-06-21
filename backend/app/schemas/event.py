from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.event import EventStatus
from app.models.application import ApplicationStatus
from app.schemas.venue import VenueOut


class EventCreate(BaseModel):
    venue_id: int
    sport_type: str | None = None
    group_link: str | None = None
    scheduled_at: datetime | None = None
    price: float | None = None
    slots_total: int = Field(ge=1, le=100)

    @field_validator("sport_type", "group_link", mode="before")
    @classmethod
    def blank_string_to_none(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("group_link")
    @classmethod
    def group_link_must_be_safe(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not (value.startswith("https://t.me/") or value.startswith("https://telegram.me/")):
            raise ValueError("Ссылка на группу должна быть Telegram-ссылкой")
        return value

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_at_must_be_in_future(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value

        scheduled_at = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        if scheduled_at <= datetime.now(timezone.utc):
            raise ValueError("Время проведения должно быть в будущем")
        return value


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


class FeedPage(BaseModel):
    items: list[EventOut]
    next_cursor: int | None = None


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
