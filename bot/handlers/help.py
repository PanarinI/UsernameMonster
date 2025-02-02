from aiogram import Router, types, F
from aiogram.filters import Command
from keyboards.main_menu import help_menu
from utils.texts import get_help_text  # Импортируем текст справки

help_router = Router()  # Создаём Router

@help_router.message(Command("help"))
async def cmd_help(message: types.Message):
    """
    Обработчик команды /help.
    """
    await message.answer(get_help_text(), parse_mode="Markdown", reply_markup=help_menu())

@help_router.callback_query(F.data == "help")
async def handle_help(query: types.CallbackQuery):
    """
    Обработчик для кнопки "Помощь".
    """
    await query.answer()  # Убираем "часики"
    await query.message.answer(get_help_text(), parse_mode="Markdown", reply_markup=help_menu())