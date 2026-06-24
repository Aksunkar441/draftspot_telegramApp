CITY_ALIASES = {
    "тараз": "Тараз",
    "taraz": "Тараз",
}


def normalize_city(city: str | None) -> str:
    value = (city or "").strip()
    if not value:
        return "Тараз"
    return CITY_ALIASES.get(value.casefold(), value[:1].upper() + value[1:])
