import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import async_session
from app.models.event import Event, EventStatus
from app.models.application import EventApplication, ApplicationStatus
from app.models.user import User
from app.bot.bot_instance import bot

REMINDER_WINDOW = timedelta(hours=2)
CHECK_INTERVAL_SECONDS = 60


async def _send_reminders_once() -> None:
    now = datetime.now(timezone.utc)
    async with async_session() as session:
        result = await session.execute(
            select(Event).where(
                Event.status.in_([EventStatus.open, EventStatus.full]),
                Event.reminder_sent.is_(False),
                Event.scheduled_at.is_not(None),
                Event.scheduled_at <= now + REMINDER_WINDOW,
                Event.scheduled_at > now,
            )
        )
        events = result.scalars().all()

        for event in events:
            applications_result = await session.execute(
                select(EventApplication).where(
                    EventApplication.event_id == event.id,
                    EventApplication.status == ApplicationStatus.accepted,
                )
            )
            participant_ids = {a.user_id for a in applications_result.scalars().all()}
            participant_ids.add(event.captain_id)

            users_result = await session.execute(select(User).where(User.id.in_(participant_ids)))
            for user in users_result.scalars().all():
                await bot.send_message(
                    user.telegram_id,
                    f"Напоминание: игра «{event.sport_type or 'без названия'}» начнётся менее чем через 2 часа!",
                )
            event.reminder_sent = True

        await session.commit()


async def reminder_loop() -> None:
    """
    Простой бесконечный цикл вместо отдельного воркера/cron — для прода
    лучше заменить на APScheduler или Celery beat, но для одного процесса
    этого достаточно. Можно добавить второй reminder_sent_1h для напоминания
    за час по аналогии.
    """
    while True:
        try:
            await _send_reminders_once()
        except Exception:
            pass
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
