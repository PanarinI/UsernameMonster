from aiogram import Router, types
from aiogram.filters import Command
from keyboards.main_menu import main_menu_kb  # Импортируем клавиатуру

start_router = Router()  # Создаём Router

@start_router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer("🔮 Привет, странник. Я Имялов — охотник за именами. Давай выловим для тебя что-то особенное?", reply_markup=main_menu_kb())




