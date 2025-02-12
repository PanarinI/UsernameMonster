from aiogram import Bot, Router, types, F
import asyncio
import logging
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from services.generate import get_available_usernames
from keyboards.generate import generate_username_kb, error_retry_kb
from .states import GenerateUsernameStates
import config
from keyboards.main_menu import main_menu_kb, back_to_main_kb
from aiogram.exceptions import TelegramRetryAfter

generate_router = Router()

@generate_router.callback_query(F.data == "generate")
async def cmd_generate_username(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Сгенерировать username".
    """
    await state.clear()  # Очищаем предыдущее состояние перед новой командой
    await asyncio.sleep(0.05)  # ✅ Даем FSM время сброситься
    await query.message.answer("Введите тему/контекст для генерации username (макс. 200 знаков):", reply_markup=back_to_main_kb())
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

    await message.answer("Введите тему/контекст для генерации username:", reply_markup=back_to_main_kb())
    await state.set_state(GenerateUsernameStates.waiting_for_context)


@generate_router.message(GenerateUsernameStates.waiting_for_context)
async def process_context_input(message: types.Message, bot: Bot, state: FSMContext):
    """
    Обработчик для введённого контекста.
    Проверяет его длину, отправляет предупреждение (если нужно), а затем запускает генерацию и проверку username.
    """
    context_text = message.text.strip()

    # ✅ Проверяем длину контекста
    if len(context_text) > config.MAX_CONTEXT_LENGTH:
        logging.warning(
            f"⚠️ Контекст слишком длинный ({len(context_text)} символов), обрезаем до {config.MAX_CONTEXT_LENGTH}.")

        # Отправляем пользователю предупреждение
        await message.answer(
            f"⚠️ Контекст слишком длинный ({len(context_text)} символов). "
            f"Обрезаю до {config.MAX_CONTEXT_LENGTH} символов."
        )

        # Обрезаем контекст перед генерацией
        context_text = context_text[:config.MAX_CONTEXT_LENGTH]

    try:
        usernames = await asyncio.wait_for(
            get_available_usernames(bot, context_text, n=config.AVAILABLE_USERNAME_COUNT),
            timeout=config.GEN_TIMEOUT
        )

        # 🛑 Если `get_available_usernames()` вернул `FLOOD_CONTROL`, то показываем сообщение и выходим в меню
        if isinstance(usernames, str) and usernames.startswith("FLOOD_CONTROL"):
            retry_seconds = int(usernames.split(":")[1])
            logging.warning(f"🚨 Блокировка API Telegram! Ожидание {retry_seconds} секунд.")

            await message.answer(
                f"⏳ Бот временно заблокирован за слишком частые запросы.\n"
                f"Попробуйте снова через {retry_seconds // 60} мин.",
                reply_markup=main_menu_kb()
            )
            await state.clear()
            return  # Прерываем процесс

    except asyncio.TimeoutError:
        logging.info("Время ожидания генерации username истекло.")
        await message.answer("Генерация username заняла слишком много времени. Попробуйте позже.", reply_markup=main_menu_kb())
        await state.clear()
        return

    # ✅ Проверяем блокировку Telegram API
    if isinstance(usernames, str) and usernames.startswith("FLOOD_CONTROL"):
        retry_after = usernames.split(":")[1]  # Извлекаем секунды
        await message.answer(
            f"🚫 Бот временно заблокирован в Telegram API из-за слишком частых запросов.\n"
            f"Попробуйте снова через {retry_after} секунд.",
            reply_markup=main_menu_kb()
        )
        await state.clear()
        return

    #
    if not usernames:
        await message.answer(
            "❌ Не удалось сгенерировать доступные username. Попробуйте снова или вернитесь в главное меню.",
            reply_markup=error_retry_kb()
        )
        return  # Завершаем выполнение

    kb_usernames = generate_username_kb(usernames)
    await message.answer(
        f"Вот сгенерированные для вас username по теме '{context_text}':",
        reply_markup=kb_usernames
    )
    await state.clear()


