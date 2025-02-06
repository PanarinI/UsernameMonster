from aiogram import Router, types
from aiogram.filters import Command
from keyboards.main_menu import main_menu  # Импортируем клавиатуру

start_router = Router()  # Создаём Router

@start_router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer("Привет! Добро пожаловать в бота. Выберите действие:", reply_markup=main_menu())




# @dp.message(Command("check"))
# async def command_2(message: types.Message):
 #   await handle_button_2(types.CallbackQuery(message=message, data="check"))

  #  @dp.message(Command("help"))
   # async def command_2(message: types.Message):
    #    await handle_button_2(types.CallbackQuery(message=message, data="help"))



