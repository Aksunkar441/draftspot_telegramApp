import asyncio
from sqlalchemy import select
from app.database import engine, async_session
from app.models.venue import Venue, VenueStatus

async def seed():
    async with async_session() as session:
        # Проверяем, есть ли уже площадки
        result = await session.execute(select(Venue))
        if result.scalars().first():
            print("Площадки уже добавлены.")
            return

        venues = [
            Venue(
                name="Центральный стадион Тараз",
                sport_type="Футбол",
                latitude=42.8964,
                longitude=71.3614,
                is_paid=True,
                price=5000.0,
                status=VenueStatus.free,
                address="ул. Толе би, 93"
            ),
            Venue(
                name="Спорткомплекс Олимпик",
                sport_type="Баскетбол",
                latitude=42.9055,
                longitude=71.3789,
                is_paid=True,
                price=3000.0,
                status=VenueStatus.free,
                address="мкр. Самал, 12"
            ),
            Venue(
                name="Дворовая площадка (8-й микрорайон)",
                sport_type="Футбол",
                latitude=42.8876,
                longitude=71.3456,
                is_paid=False,
                price=0.0,
                status=VenueStatus.free,
                address="мкр. Алатау, возле д. 15"
            ),
            Venue(
                name="Теннисный корт Тараз",
                sport_type="Теннис",
                latitude=42.9123,
                longitude=71.3912,
                is_paid=True,
                price=4000.0,
                status=VenueStatus.free,
                address="ул. Желтоксан, 55"
            ),
            Venue(
                name="Стритбольная площадка (Парк Первого Президента)",
                sport_type="Баскетбол",
                latitude=42.8932,
                longitude=71.3702,
                is_paid=False,
                price=0.0,
                status=VenueStatus.free,
                address="Парк Первого Президента"
            )
        ]
        
        session.add_all(venues)
        await session.commit()
        print("Успешно добавлено 5 тестовых площадок в Таразе!")

if __name__ == "__main__":
    asyncio.run(seed())
