from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.reply import main_menu

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\n"
        "OSINT Botga xush kelibsiz.",
        reply_markup=main_menu
    )