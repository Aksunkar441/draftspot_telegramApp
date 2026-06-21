from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event, EventStatus
from app.models.application import EventApplication, ApplicationStatus


async def accept_application(session: AsyncSession, application: EventApplication) -> tuple[bool, list[EventApplication]]:
    """
    Атомарно уменьшает количество свободных мест и принимает заявку.
    UPDATE ... WHERE slots_available > 0 выполняется одним запросом —
    PostgreSQL сам блокирует строку события на долю секунды, поэтому
    два параллельных accept() на последнее место не уйдут оба в плюс.
    Возвращает False, если мест уже не осталось. Если принятая заявка
    заняла последнее место, оставшиеся pending-заявки на это событие
    автоматически отклоняются, чтобы игроки не висели в ожидании.
    """
    result = await session.execute(
        update(Event)
        .where(Event.id == application.event_id, Event.slots_available > 0)
        .values(slots_available=Event.slots_available - 1)
        .returning(Event.id, Event.slots_available)
    )
    row = result.first()
    if row is None:
        return False, []

    now = datetime.now(timezone.utc)
    application.status = ApplicationStatus.accepted
    application.responded_at = now
    auto_declined: list[EventApplication] = []

    if row.slots_available == 0:
        event = await session.get(Event, application.event_id)
        event.status = EventStatus.full
        pending_result = await session.execute(
            select(EventApplication).where(
                EventApplication.event_id == application.event_id,
                EventApplication.status == ApplicationStatus.pending,
                EventApplication.id != application.id,
            )
        )
        auto_declined = list(pending_result.scalars().all())
        for pending_application in auto_declined:
            pending_application.status = ApplicationStatus.declined
            pending_application.responded_at = now

    await session.commit()
    return True, auto_declined


async def cancel_acceptance(session: AsyncSession, application: EventApplication) -> None:
    """Возвращает свободное место при отмене игроком или исключении капитаном."""
    if application.status == ApplicationStatus.accepted:
        await session.execute(
            update(Event)
            .where(Event.id == application.event_id)
            .values(slots_available=Event.slots_available + 1, status=EventStatus.open)
        )

    application.status = ApplicationStatus.cancelled
    application.responded_at = datetime.now(timezone.utc)
    await session.commit()


async def cancel_event(session: AsyncSession, event: Event) -> list[EventApplication]:
    """Отменяет публикацию капитаном и закрывает все активные заявки."""
    result = await session.execute(
        select(EventApplication).where(
            EventApplication.event_id == event.id,
            EventApplication.status.in_([ApplicationStatus.pending, ApplicationStatus.accepted]),
        )
    )
    active_applications = list(result.scalars().all())
    now = datetime.now(timezone.utc)

    for application in active_applications:
        application.status = ApplicationStatus.cancelled
        application.responded_at = now

    event.status = EventStatus.cancelled
    event.slots_available = 0
    await session.commit()
    return active_applications


async def complete_expired_events(session: AsyncSession) -> None:
    """Закрывает прошедшие события, чтобы они не висели в ленте и истории будущих игр."""
    now = datetime.now(timezone.utc)
    expired_events = (
        select(Event.id)
        .where(
            Event.status.in_([EventStatus.open, EventStatus.full]),
            Event.scheduled_at.is_not(None),
            Event.scheduled_at <= now,
        )
        .subquery()
    )
    await session.execute(
        update(EventApplication)
        .where(
            EventApplication.event_id.in_(select(expired_events.c.id)),
            EventApplication.status == ApplicationStatus.pending,
        )
        .values(status=ApplicationStatus.cancelled, responded_at=now)
    )
    await session.execute(
        update(Event)
        .where(
            Event.status.in_([EventStatus.open, EventStatus.full]),
            Event.scheduled_at.is_not(None),
            Event.scheduled_at <= now,
        )
        .values(status=EventStatus.completed)
    )
    await session.commit()
