from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.venue import Venue
from app.schemas.venue import VenueOut

router = APIRouter(prefix="/api/venues", tags=["venues"])


@router.get("", response_model=list[VenueOut])
async def list_venues(session: AsyncSession = Depends(get_session)):
    """
    Список площадок готовится платформой заранее (геоданные, тип игры,
    платность, статус занятости для платных кортов).
    """
    result = await session.execute(select(Venue))
    return result.scalars().all()
