from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.city import normalize_city
from app.database import get_session
from app.models.user import User
from app.models.venue import Venue
from app.schemas.venue import VenueOut

router = APIRouter(prefix="/api/venues", tags=["venues"])


@router.get("", response_model=list[VenueOut])
async def list_venues(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Список площадок готовится платформой заранее (геоданные, тип игры,
    платность, статус занятости для платных кортов).
    """
    city = normalize_city(user.city)
    result = await session.execute(
        select(Venue).where(Venue.city == city).order_by(Venue.name.asc())
    )
    return result.scalars().all()
