import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InputFile, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from image_generator import generate_images
from aiogram.types import BufferedInputFile
from aiogram.types import InputMediaPhoto

API_TOKEN = '7747562799:AAH3ip_M9ImM2KZLublIJMYPSZ-ftUoM74Q'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    cover = State()
    background = State()
    artists = State()
    release = State()
    lyrics = State()

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer(
        "🎧 *Добро пожаловать в @MUSICPICBOT!*\n\n"
        "📀 Отправь квадратную *обложку* (фото), чтобы начать.",
        parse_mode="Markdown"
    )
    await state.set_state(Form.cover)

@dp.message(Form.cover, F.photo)
async def get_cover(message: types.Message, state: FSMContext):
    photo = message.photo[-1]  # type: ignore
    path = f"temp/{message.from_user.id}_cover.jpg"  # type: ignore
    await bot.download(photo, destination=path)
    await state.update_data(cover=path)
    await message.answer(
        "🌄 Отлично! Теперь отправь *фон* (фото).",
        parse_mode="Markdown"
    )
    await state.set_state(Form.background)

@dp.message(Form.background, F.photo)
async def get_background(message: types.Message, state: FSMContext):
    photo = message.photo[-1]  # type: ignore
    path = f"temp/{message.from_user.id}_background.jpg"  # type: ignore
    await bot.download(photo, destination=path)
    await state.update_data(background=path)
    await message.answer("👥 Введи *ники артистов*:", parse_mode="Markdown")
    await state.set_state(Form.artists)

@dp.message(Form.artists)
async def get_artists(message: types.Message, state: FSMContext):
    await state.update_data(artists=message.text)
    await message.answer("🎵 Введи *название релиза*:", parse_mode="Markdown")
    await state.set_state(Form.release)

@dp.message(Form.release)
async def get_release(message: types.Message, state: FSMContext):
    await state.update_data(release=message.text)
    await message.answer("📝 Введи *текст трека*:", parse_mode="Markdown")
    await state.set_state(Form.lyrics)

@dp.message(Form.lyrics)
async def get_lyrics(message: types.Message, state: FSMContext):
    await state.update_data(lyrics=message.text)
    data = await state.get_data()

    output1, output2 = generate_images(
        cover_path=data['cover'],
        background_path=data['background'],
        artists=data['artists'],
        release=data['release'],
        lyrics=data['lyrics'],
        bot_username='@MUSICPICBOT'
    )

    media = [
        InputMediaPhoto(media=BufferedInputFile(output1.read(), filename="output1.jpg")),
        InputMediaPhoto(media=BufferedInputFile(output2.read(), filename="output2.jpg")),
    ]

    await message.answer_media_group(media)  # type: ignore
    await message.answer(
        "✅ *Готово!*\n\n📌 Чтобы создать ещё обложку, отправь */start*",
        parse_mode="Markdown"
    )
    await state.clear()


if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
