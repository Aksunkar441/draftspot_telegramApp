import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.bot_instance import bot
from app.bot.keyboards import accept_decline_keyboard
from app.models.event import Event
from app.models.user import User
from app.models.application import EventApplication

logger = logging.getLogger(__name__)


async def _send_message(chat_id: int, text: str, **kwargs) -> None:
    try:
        await bot.send_message(chat_id, text, **kwargs)
    except Exception:
        logger.exception("Failed to send Telegram notification to chat_id=%s", chat_id)


async def notify_captain_new_application(
    session: AsyncSession, event: Event, applicant: User, application_id: int
) -> None:
    captain = await session.get(User, event.captain_id)
    await _send_message(
        captain.telegram_id,
        f"Новая заявка на «{event.sport_type or 'игру'}» от {applicant.name}.",
        reply_markup=accept_decline_keyboard(application_id),
    )


async def notify_player_decision(session: AsyncSession, application: EventApplication, accepted: bool) -> None:
    player = await session.get(User, application.user_id)
    text = (
        "Капитан принял вашу заявку! Игра появилась в разделе «Предстоящие игры»."
        if accepted
        else "Капитан отклонил вашу заявку."
    )
    await _send_message(player.telegram_id, text)


async def notify_player_event_full(session: AsyncSession, application: EventApplication) -> None:
    player = await session.get(User, application.user_id)
    event = await session.get(Event, application.event_id)
    await _send_message(
        player.telegram_id,
        f"В игре «{event.sport_type or 'без названия'}» закончились свободные места. "
        "Ваша заявка отклонена автоматически.",
    )


async def notify_team_about_cancellation(session: AsyncSession, application: EventApplication) -> None:
    event = await session.get(Event, application.event_id)
    captain = await session.get(User, event.captain_id)
    player = await session.get(User, application.user_id)

    await _send_message(
        captain.telegram_id,
        f"{player.name} больше не участвует в игре «{event.sport_type or 'без названия'}». Освободилось место.",
    )
    await _send_message(
        player.telegram_id,
        f"Ваше участие в игре «{event.sport_type or 'без названия'}» отменено.",
    )


async def notify_player_event_cancelled(session: AsyncSession, application: EventApplication) -> None:
    player = await session.get(User, application.user_id)
    event = await session.get(Event, application.event_id)
    await _send_message(
        player.telegram_id,
        f"Игра «{event.sport_type or 'без названия'}» отменена капитаном.",
    )
