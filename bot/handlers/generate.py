from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from .states import GenerateUsernameStates  # Импорт состояний
from services.generate import generate_unique_username
from keyboards.generate import generate_username_kb

generate_router = Router()

@generate_router.callback_query(F.data == "generate")
async def cmd_generate_username(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Генерировать".
    Переводит бота в состояние ожидания ввода контекста.
    """
    await query.message.answer("Введите тему/контекст для генерации username:")
    await state.set_state(GenerateUsernameStates.waiting_for_context)
    await query.answer()

@generate_router.message(GenerateUsernameStates.waiting_for_context)
async def process_context_input(message: types.Message, state: FSMContext):
    """
    Обработчик для введённого контекста.
    Генерирует username и выводит результат.
    """
    context_text = message.text
    usernames = generate_unique_username(n=3, context=context_text)
    kb = generate_username_kb(usernames)
    await message.answer(
        f"Вот сгенерированные для вас username по теме '{context_text}':",
        reply_markup=kb
    )
    await state.clear()  # Сброс состояния после завершения

@generate_router.callback_query(F.data == "regenerate")
async def cmd_regenerate_username(query: types.CallbackQuery):
    """
    Обработчик для кнопки "Сгенерировать ещё раз".
    """
    await query.answer("Функция 'сгенерировать ещё раз' пока не реализована.", show_alert=False)

