from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_name = State()
    waiting_age = State()
    waiting_city = State()
    waiting_photos = State()
    waiting_description = State()
