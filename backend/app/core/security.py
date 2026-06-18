import hashlib
import hmac
from urllib.parse import parse_qsl

from app.config import settings


def validate_init_data(init_data: str) -> dict | None:
    """
    Проверяет криптографическую подпись initData, присланной Telegram Mini App.
    Возвращает распарсенные поля (user, auth_date и т.д.) или None, если подпись неверна.
    Без этой проверки кто угодно мог бы подделать свой telegram_id и выдать себя
    за другого пользователя.
    """
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    secret_key = hmac.new(b"WebAppData", settings.bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        return None

    return parsed
