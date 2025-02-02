from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.main_menu import main_menu  # Импортируем клавиатуру главного меню

common_router = Router()  # Создаём Router

@common_router.callback_query(F.data == "back_to_main")
async def cmd_back_to_main_menu(query: types.CallbackQuery):
    """
    Обработчик для кнопки "Назад в главное меню".
    """
    await query.answer()     # Отвечаем на callback_query, параметр - текст всплывающего уведомления или пусто
    await query.message.answer("Вы вернулись в главное меню:", reply_markup=main_menu())     # Отправляем пользователю главное меню