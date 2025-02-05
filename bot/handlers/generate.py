from aiogram import Bot, Router, types, F # основные инструменты для создания роутера и обработки сообщений.
from aiogram.fsm.context import FSMContext # для работы с конечными автоматами состояний (FSM)
from services.generate import get_available_usernames # функция для генерации username.
from keyboards.generate import generate_username_kb # клавиатура для отображения сгенерированных username.
from .states import GenerateUsernameStates # состояния FSM для этого роутера.
import config

generate_router = Router() # создается роутер для обработки команд, связанных с генерацией username.

@generate_router.callback_query(F.data == "generate") # Срабатывает на callback с данными "generate".
async def cmd_generate_username(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Сгенерировать username".
    """
    await query.message.answer("Введите тему/контекст для генерации username:") # Отправляет пользователю сообщение с запросом ввода темы/контекста для генерации username.
    await state.set_state(GenerateUsernameStates.waiting_for_context) # Устанавливает состояние GenerateUsernameStates.waiting_for_context.
    await query.answer() # Отправляет подтверждение (query.answer()), чтобы Telegram знал, что callback обработан.

@generate_router.message(GenerateUsernameStates.waiting_for_context) # Срабатывает, когда пользователь вводит текст в состоянии GenerateUsernameStates.waiting_for_context.
async def process_context_input(message: types.Message, bot: Bot, state: FSMContext):
    """
    Обработчик для введённого контекста.
    Генерирует и проверяет username.
    """
    context_text = message.text.strip() # Извлекает текст сообщения (context_text).
    usernames = await get_available_usernames(bot, context_text, n=config.AVAILABLE_USERNAME_COUNT) # Генерирует доступные username с помощью функции get_available_usernames
    kb = generate_username_kb(usernames)
    await message.answer(
        f"Вот сгенерированные для вас username по теме '{context_text}':",
        reply_markup=kb
    )
    await state.clear()