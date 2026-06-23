from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.event import Event, EventStatus
from app.schemas.event import EventOut


def event_unavailable_reason(event: Event) -> str | None:
    if event.status == EventStatus.cancelled:
        return "Игра отменена"
    if event.status == EventStatus.completed:
        return "Игра закончилась"
    if event.status == EventStatus.full or event.slots_available <= 0:
        return "Мест больше нет"
    return None


class FavoriteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    event: EventOut
    is_available: bool
    unavailable_reason: str | None = None

    @classmethod
    def from_favorite(cls, favorite) -> "FavoriteOut":
        reason = event_unavailable_reason(favorite.event)
        return cls(
            id=favorite.id,
            created_at=favorite.created_at,
            event=favorite.event,
            is_available=reason is None,
            unavailable_reason=reason,
        )
