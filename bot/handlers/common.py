from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

common_router = Router()  # Создаём Router

@common_router.callback_query(F.data == "back_to_main")
async def cmd_back_to_main_menu(query: types.CallbackQuery):
    """
    Обработчик для кнопки "Назад в главное меню".
    """
    await query.answer("Возврат в главное меню пока не реализован.", show_alert=False)