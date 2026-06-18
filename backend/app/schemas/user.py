from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    name: str
    age: int | None
    photos: list[str]
    city: str
    bio: str | None
