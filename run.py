import os
import asyncio
from typing import Callable, Any, Awaitable
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from pdf_functions import PDF

load_dotenv()
TOKEN = os.getenv("KEY")

dp = Dispatcher()


class AlbumMiddleware(BaseMiddleware):
    """Посредник для автоматического объединения фото из альбомов (медиагрупп)"""

    def __init__(self, latency: float = 0.5):
        self.latency = latency
        self.album_data = {}

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        # if message is not an album part
        if not event.media_group_id:
            await handler(event, data)
            return

        try:
            self.album_data[event.media_group_id].append(event)
        except KeyError:
            self.album_data[event.media_group_id] = [event]
            # waiting a lil bit so telegram sends everything without a loss
            await asyncio.sleep(self.latency)

            # is an album ready?
            data["_is_last"] = True
            data["album"] = self.album_data[event.media_group_id]
            await handler(event, data)

            if event.media_group_id in self.album_data:
                del self.album_data[event.media_group_id]


# status switcher
class PDFStates(StatesGroup):
    collecting = State()  # mode for one by one
    waiting_for_filename = State()  # mode for name of file


# this is section for keyboards
def get_start_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="➕ Режим по одной (по порядку)")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def get_collecting_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Сгенерировать PDF")
    builder.button(text="❌ Отмена")
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)


async def download_photo_bytes(message: Message, bot: Bot) -> bytes:
    photo = message.photo[-1]
    photo_file = await bot.download(photo)
    return photo_file.getvalue()


@dp.message(Command("start"))
@dp.message(Command("cancel"))
@dp.message(F.text == "❌ Отмена")
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Способ 1: Просто отправь мне пачку фоток разом (как альбом). Я автоматически соберу их в PDF.\n\n"
        "Способ 2 (По порядку): Нажми на кнопку ниже, отправляй фото строго по очереди, а когда закончишь — нажми кнопку генерации.",
        reply_markup=get_start_keyboard(),
    )


@dp.message(F.text == "➕ Режим по одной (по порядку)")
async def start_one_by_one(message: Message, state: FSMContext) -> None:
    await state.set_state(PDFStates.collecting)
    await state.update_data(photos=[])
    await message.answer(
        "Отправляйте фотографии по очереди, они сохранят строгий порядок отправки).\n"
        "Как закончите - нажмите кнопку 'Сгенерировать PDF'",
        reply_markup=get_collecting_keyboard(),
    )


@dp.message(F.media_group_id, F.photo)
async def handle_album(
    message: Message, album: list[Message], state: FSMContext, bot: Bot
):
    current_state = await state.get_state()

    if current_state == PDFStates.collecting:
        data = await state.get_data()
        photos = data.get("photos", [])
        for msg in album:
            photo_bytes = await download_photo_bytes(msg, bot)
            photos.append(photo_bytes)
        await state.update_data(photos=photos)
        await message.answer(
            f"Добавил {len(album)} фото из альбома в вашу очередь. Всего в очереди: {len(photos)}"
        )
        return

    await message.answer("Получил альбом! Скачиваю фотографии...")
    downloaded_photos = []
    for msg in album:
        photo_bytes = await download_photo_bytes(msg, bot)
        downloaded_photos.append(photo_bytes)

    await state.update_data(photos=downloaded_photos)
    await state.set_state(PDFStates.waiting_for_filename)
    await message.answer(
        f"Успешно скачал {len(downloaded_photos)} фото! Как назвать готовый PDF файл?",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(PDFStates.collecting, F.photo, ~F.media_group_id)
async def handle_single_photo_collecting(message: Message, state: FSMContext, bot: Bot):
    photo_bytes = await download_photo_bytes(message, bot)
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(photo_bytes)
    await state.update_data(photos=photos)
    await message.answer(
        f"Фото #{len(photos)} добавлено! Отправляйте следующее или нажмите 'Сгенерировать PDF'."
    )


@dp.message(F.photo, ~F.media_group_id)
async def handle_sole_photo_instant(message: Message, state: FSMContext, bot: Bot):
    await message.answer("Получил фото! Скачиваю...")
    photo_bytes = await download_photo_bytes(message, bot)
    await state.update_data(photos=[photo_bytes])
    await state.set_state(PDFStates.waiting_for_filename)
    await message.answer(
        "Как назвать готовый PDF файл?", reply_markup=ReplyKeyboardRemove()
    )


@dp.message(PDFStates.collecting, F.text == "✅ Сгенерировать PDF")
@dp.message(PDFStates.collecting, Command("done"))
async def done_collecting(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if not photos:
        await message.answer("Вы еще не отправили ни одного фото!")
        return
    await state.set_state(PDFStates.waiting_for_filename)
    await message.answer(
        f"Собрано {len(photos)} фото. Как назвать готовый PDF файл?",
        reply_markup=ReplyKeyboardRemove(),
    )


# catching filename and pdf
@dp.message(PDFStates.waiting_for_filename, F.text, ~F.text.startswith("/"))
async def process_filename(message: Message, state: FSMContext):
    raw_filename = message.text.strip()
    filename = "".join(
        c for c in raw_filename if c.isalnum() or c in (" ", "_", "-")
    ).strip()
    if not filename:
        filename = "document"

    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    await message.answer(f"Сборка файла '{filename}'...")

    data = await state.get_data()
    photos = data.get("photos", [])

    pdf_tool = PDF()
    try:
        pdf_bytes = pdf_tool.create_pdf_from_memory(photos)
        if pdf_bytes:
            pdf_file_to_send = BufferedInputFile(pdf_bytes, filename=filename)
            await message.answer_document(
                pdf_file_to_send, reply_markup=get_start_keyboard()
            )
        else:
            await message.answer(
                "Произошла ошибка при сборке PDF.", reply_markup=get_start_keyboard()
            )
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=get_start_keyboard())

    await state.clear()


# if we got text for some reason and not a photo???
@dp.message(PDFStates.collecting, ~F.photo)
async def collecting_text_fallback(message: Message):
    await message.answer(
        "Сейчас идет поштучный сбор фото. Пожалуйста, отправляйте только фотографии.\n"
        "Когда закончите, нажмите '✅ Сгенерировать PDF' или '❌ Отмена' для выхода.",
        reply_markup=get_collecting_keyboard(),
    )


# other messages
@dp.message(F.text)
async def all_message(message: Message) -> None:
    await message.answer(
        "Отправьте мне альбом фотографий или нажмите кнопку ниже для поштучного сбора.",
        reply_markup=get_start_keyboard(),
    )


async def main() -> None:
    bot = Bot(token=TOKEN)

    dp.message.middleware(AlbumMiddleware(latency=0.5))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
