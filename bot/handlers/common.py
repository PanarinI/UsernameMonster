from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import main_menu_kb  # Импортируем клавиатуру главного меню

common_router = Router()

@common_router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Назад в меню".
    Сбрасывает текущее состояние и отправляет главное меню.
    """
    await query.answer()  # Отвечаем на callback_query
    # Сброс состояния пользователя, если оно задано
    await state.clear()
    await query.message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=main_menu_kb()
    )
    await query.answer()  # Telegram требует подтверждения



