from aiogram import Bot, Router, types, F
import asyncio
import logging
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from services.generate import get_available_usernames
from keyboards.generate import generate_username_kb, error_retry_kb
from .states import GenerateUsernameStates
import config
from keyboards.main_menu import main_menu

generate_router = Router()

@generate_router.callback_query(F.data == "generate")
async def cmd_generate_username(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Сгенерировать username".
    """
    await state.clear()  # Очищаем предыдущее состояние перед новой командой
    await asyncio.sleep(0.05)  # ✅ Даем FSM время сброситься
    await query.message.answer("Введите тему/контекст для генерации username:")
    await state.set_state(GenerateUsernameStates.waiting_for_context)
    await query.answer()  # Telegram требует подтверждения, что callback обработан.


@generate_router.message(Command("generate")) # фильтр чтобы /generate срабатывал независимо от состояния
async def cmd_generate_slash(message: types.Message, state: FSMContext):
    """
    Обработчик для команды /generate.
    Вызывает ту же логику, что и inline-кнопка.
    """
    await state.clear()  # ⛔️ Принудительно очищаем ВСЕ состояния
    await asyncio.sleep(0.1)  # 🔄 Даём FSM время сброситься

    await message.answer("Введите тему/контекст для генерации username:")
    await state.set_state(GenerateUsernameStates.waiting_for_context)


@generate_router.message(GenerateUsernameStates.waiting_for_context)
async def process_context_input(message: types.Message, bot: Bot, state: FSMContext):
    """
    Обработчик для введённого контекста.
    Генерирует и проверяет username.
    """
    context_text = message.text.strip()
    try:
        usernames = await asyncio.wait_for(
            get_available_usernames(bot, context_text, n=config.AVAILABLE_USERNAME_COUNT),
            timeout=config.GEN_TIMEOUT
        )
    except asyncio.TimeoutError:
        logging.info("Время ожидания генерации username истекло.")
        await message.answer("Генерация username заняла слишком много времени. Попробуйте позже.", reply_markup=main_menu())
        await state.clear()
        return

    if not usernames:
        await message.answer(
            "❌ Не удалось сгенерировать доступные username. Попробуйте снова или вернитесь в главное меню.",
            reply_markup=error_retry_kb()
        )
        return  # Завершаем выполнение

    kb = generate_username_kb(usernames)
    await message.answer(
        f"Вот сгенерированные для вас username по теме '{context_text}':",
        reply_markup=kb
    )
    await state.clear()
