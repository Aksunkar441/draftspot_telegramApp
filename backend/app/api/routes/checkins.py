from datetime import date
from math import atan2, cos, radians, sin, sqrt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_session
from app.models.checkin import VenueCheckin
from app.models.user import User
from app.models.venue import Venue
from app.schemas.checkin import CheckinCreate, CheckinResult

CHECKIN_RADIUS_METERS = 200

router = APIRouter(prefix="/api/checkins", tags=["checkins"])


@router.post("", response_model=CheckinResult)
async def create_checkin(
    payload: CheckinCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    venue = await session.get(Venue, payload.venue_id)
    if venue is None:
        raise HTTPException(status_code=404, detail="Площадка не найдена")

    distance_meters = round(
        distance_between_meters(
            payload.latitude,
            payload.longitude,
            venue.latitude,
            venue.longitude,
        )
    )
    if distance_meters > CHECKIN_RADIUS_METERS:
        return CheckinResult(
            checked_in=False,
            radius_meters=CHECKIN_RADIUS_METERS,
            distance_meters=distance_meters,
            checkin=None,
        )

    today = date.today()
    existing = await session.scalar(
        select(VenueCheckin).where(
            VenueCheckin.user_id == user.id,
            VenueCheckin.venue_id == venue.id,
            VenueCheckin.checked_date == today,
        )
    )
    if existing is not None:
        return CheckinResult(
            checked_in=True,
            radius_meters=CHECKIN_RADIUS_METERS,
            distance_meters=existing.distance_meters,
            checkin=existing,
        )

    checkin = VenueCheckin(
        user_id=user.id,
        venue_id=venue.id,
        checked_date=today,
        latitude=payload.latitude,
        longitude=payload.longitude,
        distance_meters=distance_meters,
    )
    session.add(checkin)
    await session.commit()
    await session.refresh(checkin)

    return CheckinResult(
        checked_in=True,
        radius_meters=CHECKIN_RADIUS_METERS,
        distance_meters=distance_meters,
        checkin=checkin,
    )


def distance_between_meters(lat_a: float, lng_a: float, lat_b: float, lng_b: float) -> float:
    delta_lat = radians(lat_b - lat_a)
    delta_lng = radians(lng_b - lng_a)
    a = (
        sin(delta_lat / 2) ** 2
        + cos(radians(lat_a)) * cos(radians(lat_b)) * sin(delta_lng / 2) ** 2
    )
    return 6_371_000 * 2 * atan2(sqrt(a), sqrt(1 - a))
