from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_session
from app.models.event import Event, EventStatus
from app.models.favorite import EventFavorite
from app.models.user import User
from app.schemas.favorite import FavoriteOut
from app.services import event_service

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteOut])
async def list_favorites(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await event_service.complete_expired_events(session)
    result = await session.execute(
        select(EventFavorite)
        .options(selectinload(EventFavorite.event).selectinload(Event.venue))
        .join(EventFavorite.event)
        .where(EventFavorite.user_id == user.id)
        .order_by(EventFavorite.created_at.desc())
    )
    return [FavoriteOut.from_favorite(favorite) for favorite in result.scalars().all()]


@router.post("/{event_id}", response_model=FavoriteOut)
async def add_favorite(
    event_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await event_service.complete_expired_events(session)
    event = await session.get(Event, event_id, options=[selectinload(Event.venue)])
    if event is None or event.venue.city != user.city:
        raise HTTPException(404, "Событие не найдено")
    if event.captain_id == user.id:
        raise HTTPException(400, "Собственную публикацию нельзя добавить в избранное")
    if event.status == EventStatus.cancelled:
        raise HTTPException(400, "Отмененную игру нельзя добавить в избранное")

    favorite = EventFavorite(event_id=event_id, user_id=user.id)
    session.add(favorite)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()

    result = await session.execute(
        select(EventFavorite)
        .options(selectinload(EventFavorite.event).selectinload(Event.venue))
        .where(EventFavorite.event_id == event_id, EventFavorite.user_id == user.id)
    )
    favorite = result.scalar_one()

    return FavoriteOut.from_favorite(favorite)


@router.delete("/{event_id}")
async def remove_favorite(
    event_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(EventFavorite).where(EventFavorite.event_id == event_id, EventFavorite.user_id == user.id)
    )
    favorite = result.scalar_one_or_none()
    if favorite is None:
        return {"status": "not_found"}

    await session.delete(favorite)
    await session.commit()
    return {"status": "removed"}
