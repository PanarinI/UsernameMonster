from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.main_menu import main_menu  # Импортируем клавиатуру главного меню

common_router = Router()

@common_router.callback_query(F.data == "back_to_main")
async def cmd_back_to_main_menu(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Назад в главное меню".
    Сбрасывает текущее состояние и отправляет главное меню.
    """
    await query.answer()  # Отвечаем на callback_query
    # Сброс состояния пользователя, если оно задано
    await state.clear()
    await query.message.answer("Вы вернулись в главное меню:", reply_markup=main_menu())