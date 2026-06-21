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

    application.status = ApplicationStatus.accepted
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
    application.responded_at = None
    await session.commit()
