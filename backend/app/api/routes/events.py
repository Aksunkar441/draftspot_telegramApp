from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_session
from app.models.event import Event, EventStatus
from app.models.application import EventApplication, ApplicationStatus
from app.models.user import User
from app.models.venue import Venue
from app.schemas.event import EventOut, EventCreate, EventWithApplicants, ApplicantOut, FeedPage
from app.services import event_service
from app.services.notification_service import notify_captain_new_application, notify_player_event_cancelled

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/feed", response_model=FeedPage)
async def get_feed(
    limit: int = Query(default=10, ge=1, le=20),
    cursor: int | None = Query(default=None, ge=1),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Лента публикаций: открытые сборы, которые пользователь ещё не создал
    сам и на которые ещё не подавал заявку. Именно по этому списку
    фронтенд листает карточки "присоединиться / смотреть дальше".
    """
    await event_service.complete_expired_events(session)
    application = aliased(EventApplication)

    stmt = (
        select(Event)
        .options(selectinload(Event.venue))
        .join(Event.venue)
        .outerjoin(
            application,
            and_(
                application.event_id == Event.id,
                application.user_id == user.id,
            ),
        )
        .where(
            Event.status == EventStatus.open,
            Event.captain_id != user.id,
            Venue.city == user.city,
            application.id.is_(None),
        )
        .order_by(Event.id.desc())
        .limit(limit + 1)
    )
    if cursor is not None:
        stmt = stmt.where(Event.id < cursor)

    result = await session.execute(stmt)
    events = list(result.scalars().all())
    has_more = len(events) > limit
    items = events[:limit]
    next_cursor = items[-1].id if has_more and items else None
    return FeedPage(items=items, next_cursor=next_cursor)


@router.get("/my", response_model=list[EventOut])
async def my_events(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Слот «Мои публикации» — события, где текущий пользователь капитан."""
    await event_service.complete_expired_events(session)
    result = await session.execute(
        select(Event)
        .options(selectinload(Event.venue))
        .where(Event.captain_id == user.id, Event.status != EventStatus.cancelled)
        .order_by(Event.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=EventOut)
async def create_event(
    payload: EventCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if payload.slots_total < 1 or payload.slots_total > 100:
        raise HTTPException(400, "Количество игроков должно быть от 1 до 100")

    venue = await session.get(Venue, payload.venue_id)
    if venue is None or venue.city != user.city:
        raise HTTPException(400, "Поле недоступно")

    event = Event(
        captain_id=user.id,
        venue_id=payload.venue_id,
        sport_type=payload.sport_type,
        group_link=payload.group_link,
        scheduled_at=payload.scheduled_at,
        price=payload.price,
        slots_total=payload.slots_total,
        slots_available=payload.slots_total,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event, attribute_names=["venue"])
    return event


@router.get("/{event_id}", response_model=EventWithApplicants)
async def get_event(
    event_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await event_service.complete_expired_events(session)
    event = await session.get(
        Event,
        event_id,
        options=[
            selectinload(Event.venue),
            selectinload(Event.applications).selectinload(EventApplication.user),
        ],
    )
    if event is None:
        raise HTTPException(404, "Событие не найдено")

    is_captain = event.captain_id == user.id
    existing_application = await session.execute(
        select(EventApplication).where(
            EventApplication.event_id == event.id,
            EventApplication.user_id == user.id,
        )
    )
    has_application = existing_application.scalar_one_or_none() is not None
    is_visible_open_event = event.status == EventStatus.open and event.venue.city == user.city

    if not (is_captain or has_application or is_visible_open_event):
        raise HTTPException(404, "Событие не найдено")

    return EventWithApplicants(
        **EventOut.model_validate(event).model_dump(),
        applicants=[ApplicantOut.from_application(a) for a in event.applications] if is_captain else [],
    )


@router.post("/{event_id}/join")
async def join_event(
    event_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Игрок жмёт «Присоединиться». Заявка уходит капитану в статусе pending —
    окончательное решение принимает капитан через accept/decline.
    """
    await event_service.complete_expired_events(session)
    event = await session.get(Event, event_id, options=[selectinload(Event.venue)])
    if event is None or event.status != EventStatus.open:
        raise HTTPException(400, "Событие недоступно для заявок")
    if event.venue.city != user.city:
        raise HTTPException(400, "Событие недоступно в вашем городе")
    if event.slots_available <= 0:
        event.status = EventStatus.full
        await session.commit()
        raise HTTPException(400, "Свободные места закончились")
    if event.captain_id == user.id:
        raise HTTPException(400, "Нельзя подать заявку на собственную публикацию")

    existing = await session.execute(
        select(EventApplication).where(
            EventApplication.event_id == event_id, EventApplication.user_id == user.id
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(400, "Заявка уже отправлена")

    application = EventApplication(event_id=event_id, user_id=user.id, status=ApplicationStatus.pending)
    session.add(application)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(400, "Заявка уже отправлена") from None
    await session.refresh(application)

    await notify_captain_new_application(session, event, user, application.id)
    return {"status": "pending"}


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    event = await session.get(Event, event_id)
    if event is None or event.captain_id != user.id:
        raise HTTPException(404, "Событие не найдено")
    cancelled_applications = await event_service.cancel_event(session, event)
    for application in cancelled_applications:
        await notify_player_event_cancelled(session, application)
    return {"status": "cancelled"}
