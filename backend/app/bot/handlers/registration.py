from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database import async_session
from app.models.user import User
from app.bot.states import Registration
from app.bot.keyboards import done_uploading_photos_keyboard, skip_description_keyboard, open_app_keyboard

router = Router()


@router.message(Registration.waiting_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Registration.waiting_age)
    await message.answer("Сколько вам лет?")


@router.message(Registration.waiting_age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите возраст числом, пожалуйста.")
        return
    await state.update_data(age=int(message.text), photos=[])
    await state.set_state(Registration.waiting_photos)
    await message.answer(
        "Отправьте одно или несколько фото. Когда закончите — нажмите «Готово».",
        reply_markup=done_uploading_photos_keyboard(),
    )


@router.message(Registration.waiting_photos, F.photo)
async def process_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(f"Фото сохранено ({len(photos)}). Можете отправить ещё или нажать «Готово».")


@router.callback_query(Registration.waiting_photos, F.data == "photos_done")
async def finish_photos(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("photos"):
        await callback.answer("Загрузите хотя бы одно фото", show_alert=True)
        return
    await state.set_state(Registration.waiting_description)
    await callback.message.edit_text("Фото сохранены ✅")
    await callback.message.answer(
        "Расскажите немного о себе (или нажмите «Пропустить»).",
        reply_markup=skip_description_keyboard(),
    )
    await callback.answer()


async def _finalize_registration(message: Message, state: FSMContext, bio: str | None):
    data = await state.get_data()
    async with async_session() as session:
        user = User(
            telegram_id=message.chat.id,
            name=data["name"],
            age=data["age"],
            photos=data["photos"],
            bio=bio,
        )
        session.add(user)
        await session.commit()
    await state.clear()
    await message.answer(
        "Регистрация завершена! Открывайте приложение, чтобы увидеть ленту игр.",
        reply_markup=open_app_keyboard(),
    )


@router.message(Registration.waiting_description)
async def process_description(message: Message, state: FSMContext):
    await _finalize_registration(message, state, bio=message.text)


@router.callback_query(Registration.waiting_description, F.data == "skip_description")
async def skip_description(callback: CallbackQuery, state: FSMContext):
    await _finalize_registration(callback.message, state, bio=None)
    await callback.answer()
