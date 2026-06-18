from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from app.database import async_session
from app.models.user import User
from app.bot.states import Registration
from app.bot.keyboards import open_app_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Первый шаг записи пользователя: имя, возраст, фото (одно или несколько),
    описание (можно пропустить). Город по умолчанию — Тараз, без выбора
    на этом этапе.
    """
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = result.scalar_one_or_none()

    if user is not None:
        await message.answer(
            f"С возвращением, {user.name}! Открывайте приложение, чтобы посмотреть ленту игр.",
            reply_markup=open_app_keyboard(),
        )
        return

    await state.set_state(Registration.waiting_name)
    await message.answer("Добро пожаловать! Как вас зовут?")
