import os
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command
from aiogram.types import Message

import pdf_functions

load_dotenv()

TOKEN = os.getenv("KEY")

dp = Dispatcher()


router = Router()

# Command handler
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Отошлите фотки для конвертации в ПДФ файл. ")

@dp.message(F.text)
async def all_message(message: Message) -> None:
    await message.answer("Отошлите фотки для конвертации в ПДФ файл. ")



async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
