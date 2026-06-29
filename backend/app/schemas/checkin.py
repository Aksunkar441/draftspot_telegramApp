from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CheckinCreate(BaseModel):
    venue_id: int
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class CheckinOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    venue_id: int
    checked_date: date
    distance_meters: int
    created_at: datetime


class CheckinResult(BaseModel):
    checked_in: bool
    radius_meters: int
    distance_meters: int
    checkin: CheckinOut | None = None
