import json

from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import validate_init_data
from app.database import get_session
from app.models.user import User


async def get_current_user(
    x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Все защищённые эндпоинты Mini App требуют заголовок X-Telegram-Init-Data —
    это window.Telegram.WebApp.initData, отправленный фронтендом как есть.
    Подпись проверяется здесь, а не доверяется напрямую от клиента.
    """
    parsed = validate_init_data(x_telegram_init_data)
    if parsed is None:
        raise HTTPException(status_code=401, detail="Невалидная подпись Telegram")

    telegram_user = json.loads(parsed["user"])
    telegram_id = telegram_user["id"]

    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не зарегистрирован, начните диалог с ботом командой /start",
        )
    return user
