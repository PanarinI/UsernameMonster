from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from services.generate import generate_unique_username # Импорт функции генерации (заглушка)
from keyboards.generate import generate_username_kb # Импорт функции формирования клавиатуры для результатов генерации

# Создаём роутер для генерации
generate_router = Router()

# Определяем состояния для генерации username
class GenerateUsernameStates(StatesGroup):
    waiting_for_context = State()

@generate_router.callback_query(F.data == "generate")
async def cmd_generate_username(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Сгенерировать username".
    Вместо мгновенной генерации запрашиваем ввод контекста.
    """
    await query.message.answer("Введите тему/контекст для генерации username:")
    await state.set_state(GenerateUsernameStates.waiting_for_context)
    await query.answer()

@generate_router.message(GenerateUsernameStates.waiting_for_context)
async def process_context_input(message: types.Message, state: FSMContext):
    """
    Обработчик, получающий введённый пользователем контекст и генерирующий username.
    """
    context_text = message.text
    usernames = generate_unique_username(n=3, context=context_text)  # Заглушка
    kb = generate_username_kb(usernames)
    await message.answer(
        f"Вот сгенерированные для вас username по теме '{context_text}':",
        reply_markup=kb
    )
    await state.clear()

@generate_router.callback_query(F.data == "regenerate")
async def cmd_regenerate_username(query: types.CallbackQuery):
    """
    Обработчик для кнопки "Сгенерировать ещё раз".
    """
    await query.answer("Функция 'сгенерировать ещё раз' пока не реализована.", show_alert=False)

#@generate_router.callback_query(F.data == "back_to_main")
#async def cmd_back_to_main_menu(query: types.CallbackQuery):
#    """
#    Обработчик для кнопки "Назад в главное меню".
#    """
#    await query.answer("Возврат в главное меню пока не реализован.", show_alert=False)