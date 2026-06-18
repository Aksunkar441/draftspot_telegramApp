from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database import async_session
from app.models.application import EventApplication, ApplicationStatus
from app.services import event_service
from app.services.notification_service import notify_player_decision

router = Router()


@router.callback_query(F.data.startswith("accept:"))
async def accept_from_chat(callback: CallbackQuery):
    """
    Капитан может принять заявку прямо из уведомления в чате с ботом,
    не открывая Mini App. Логика та же атомарная функция accept_application,
    что используется и в FastAPI-роуте.
    """
    application_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        application = await session.get(EventApplication, application_id)
        if application is None or application.status != ApplicationStatus.pending:
            await callback.answer("Заявка уже обработана", show_alert=True)
            return
        success = await event_service.accept_application(session, application)
        if not success:
            await callback.answer("Свободные места закончились", show_alert=True)
            return
        await notify_player_decision(session, application, accepted=True)
    await callback.message.edit_text("Заявка принята ✅")
    await callback.answer()


@router.callback_query(F.data.startswith("decline:"))
async def decline_from_chat(callback: CallbackQuery):
    application_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        application = await session.get(EventApplication, application_id)
        if application is None or application.status != ApplicationStatus.pending:
            await callback.answer("Заявка уже обработана", show_alert=True)
            return
        application.status = ApplicationStatus.declined
        await session.commit()
        await notify_player_decision(session, application, accepted=False)
    await callback.message.edit_text("Заявка отклонена ❌")
    await callback.answer()
