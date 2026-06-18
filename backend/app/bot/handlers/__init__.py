from app.bot.handlers.start import router as start_router
from app.bot.handlers.registration import router as registration_router
from app.bot.handlers.captain_actions import router as captain_actions_router

routers = [start_router, registration_router, captain_actions_router]
