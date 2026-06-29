from contextlib import asynccontextmanager

from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.bot.bot_instance import bot, dp
from app.bot.handlers import routers
from app.api.routes import users, venues, events, applications, favorites, checkins

for r in routers:
    dp.include_router(r)


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_url = settings.webhook_base_url.rstrip("/") + settings.webhook_path
    await bot.set_webhook(webhook_url)
    yield
    await bot.session.close()


app = FastAPI(
    title="Sport Meetup API",
    lifespan=None if settings.serverless else lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(venues.router)
app.include_router(events.router)
app.include_router(applications.router)
app.include_router(favorites.router)
app.include_router(checkins.router)


@app.post(settings.webhook_path)
async def telegram_webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/health")
async def health():
    return {"status": "ok"}
