from pydantic import BaseModel, ConfigDict

from app.models.venue import VenueStatus


class VenueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sport_type: str | None
    latitude: float
    longitude: float
    is_paid: bool
    price: float | None
    status: VenueStatus
    address: str | None
