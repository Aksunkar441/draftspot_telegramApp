from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_session
from app.models.event import Event, EventStatus
from app.models.application import EventApplication, ApplicationStatus
from app.models.user import User
from app.schemas.event import EventOut, EventCreate, EventWithApplicants, ApplicantOut
from app.services.notification_service import notify_captain_new_application

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/feed", response_model=list[EventOut])
async def get_feed(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Лента публикаций: открытые сборы, которые пользователь ещё не создал
    сам и на которые ещё не подавал заявку. Именно по этому списку
    фронтенд листает карточки "присоединиться / смотреть дальше".
    """
    already_applied = select(EventApplication.event_id).where(EventApplication.user_id == user.id)

    result = await session.execute(
        select(Event)
        .options(selectinload(Event.venue))
        .where(
            Event.status == EventStatus.open,
            Event.captain_id != user.id,
            Event.id.not_in(already_applied),
        )
        .order_by(Event.created_at.desc())
    )
    return result.scalars().all()


@router.get("/my", response_model=list[EventOut])
async def my_events(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Слот «Мои публикации» — события, где текущий пользователь капитан."""
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
async def get_event(event_id: int, session: AsyncSession = Depends(get_session)):
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

    return EventWithApplicants(
        **EventOut.model_validate(event).model_dump(),
        applicants=[ApplicantOut.from_application(a) for a in event.applications],
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
    event = await session.get(Event, event_id)
    if event is None or event.status != EventStatus.open:
        raise HTTPException(400, "Событие недоступно для заявок")
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
    await session.commit()
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
    event.status = EventStatus.cancelled
    await session.commit()
    return {"status": "cancelled"}
