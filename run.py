import os
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

load_dotenv()

TOKEN = os.getenv("KEY")

dp = Dispatcher()


# Command handler
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Отошлите фотки для конвертации в ПДФ файл. ")


# Run the bot
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
