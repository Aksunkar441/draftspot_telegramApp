from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_session
from app.models.application import EventApplication, ApplicationStatus
from app.models.event import Event
from app.models.user import User
from app.schemas.application import ApplicationOut
from app.services import event_service
from app.services.notification_service import notify_player_decision, notify_team_about_cancellation

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("/pending", response_model=list[ApplicationOut])
async def my_pending(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Слот «К кому присоединился» — мои заявки, ожидающие ответа капитана."""
    result = await session.execute(
        select(EventApplication)
        .options(selectinload(EventApplication.event).selectinload(Event.venue))
        .where(EventApplication.user_id == user.id, EventApplication.status == ApplicationStatus.pending)
    )
    return result.scalars().all()


@router.get("/upcoming", response_model=list[ApplicationOut])
async def my_upcoming(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Слот «Предстоящие игры» — заявки, принятые капитаном."""
    result = await session.execute(
        select(EventApplication)
        .options(selectinload(EventApplication.event).selectinload(Event.venue))
        .where(EventApplication.user_id == user.id, EventApplication.status == ApplicationStatus.accepted)
    )
    return result.scalars().all()


async def _get_application_for_captain(session: AsyncSession, application_id: int, captain_id: int) -> EventApplication:
    application = await session.get(
        EventApplication, application_id, options=[selectinload(EventApplication.event)]
    )
    if application is None or application.event.captain_id != captain_id:
        raise HTTPException(404, "Заявка не найдена")
    return application


@router.post("/{application_id}/accept")
async def accept(
    application_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Капитан принимает заявку. Уменьшение свободных мест — атомарная
    операция на уровне БД (см. event_service.accept_application),
    поэтому одновременное нажатие "Принять" на двух заявках при одном
    свободном месте не приведёт к перебору состава.
    """
    application = await _get_application_for_captain(session, application_id, user.id)
    if application.status != ApplicationStatus.pending:
        raise HTTPException(400, "Заявка уже обработана")

    success = await event_service.accept_application(session, application)
    if not success:
        raise HTTPException(400, "Свободные места закончились")

    await notify_player_decision(session, application, accepted=True)
    return {"status": "accepted"}


@router.post("/{application_id}/decline")
async def decline(
    application_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    application = await _get_application_for_captain(session, application_id, user.id)
    if application.status != ApplicationStatus.pending:
        raise HTTPException(400, "Заявка уже обработана")

    application.status = ApplicationStatus.declined
    application.responded_at = None
    await session.commit()

    await notify_player_decision(session, application, accepted=False)
    return {"status": "declined"}


@router.post("/{application_id}/cancel")
async def cancel_by_player(
    application_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Игрок отменяет своё участие — как из слота «Ожидание», так и из
    «Предстоящих игр». Если заявка была принята, освобождённое место
    возвращается в событие и команда уведомляется.
    """
    application = await session.get(EventApplication, application_id)
    if application is None or application.user_id != user.id:
        raise HTTPException(404, "Заявка не найдена")

    was_accepted = application.status == ApplicationStatus.accepted
    await event_service.cancel_acceptance(session, application)

    if was_accepted:
        await notify_team_about_cancellation(session, application)

    return {"status": "cancelled"}


@router.post("/{application_id}/kick")
async def kick_player(
    application_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Капитан исключает игрока из своей команды — место освобождается."""
    application = await _get_application_for_captain(session, application_id, user.id)
    if application.status != ApplicationStatus.accepted:
        raise HTTPException(400, "Можно исключить только принятого игрока")

    await event_service.cancel_acceptance(session, application)
    await notify_team_about_cancellation(session, application)
    return {"status": "kicked"}
