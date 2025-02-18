import logging
import asyncio
from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from services.generate import get_available_usernames
from keyboards.generate import generate_username_kb, error_retry_kb, styles_kb
from .states import GenerateUsernameStates
import config
from keyboards.main_menu import main_menu_kb, back_to_main_kb
from aiogram.exceptions import TelegramRetryAfter

generate_router = Router()


### ✅ 1. ОБРАБОТЧИК КНОПКИ "Сгенерировать username"
@generate_router.callback_query(F.data == "generate")
async def cmd_generate_username(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Сгенерировать username".
    """
    logging.info(f"📩 Нажата кнопка 'Сгенерировать username' от {query.from_user.username} (id={query.from_user.id})")

    await state.clear()  # Очищаем состояние перед новой командой
    await asyncio.sleep(0.05)  # ✅ Даем FSM время сброситься
    await query.message.answer(
        "🔮 О чём должно говорить имя? Опиши тему, и я поймаю три уникальных имени.\n"
        "📖 <i>Например: «загадки истории», «фиолетовые котики», да что угодно</i>",
        parse_mode="HTML",
        reply_markup=back_to_main_kb()
    )

    await state.set_state(GenerateUsernameStates.waiting_for_context)
    await query.answer()  # Telegram требует подтверждения, что callback обработан.


### ✅ 2. ОБРАБОТЧИК КОМАНДЫ /generate
@generate_router.message(Command("generate"))  # Фильтр чтобы /generate срабатывал независимо от состояния
async def cmd_generate_slash(message: types.Message, state: FSMContext):
    """
    Обработчик для команды /generate.
    """
    logging.info(f"📩 Команда /generate от {message.from_user.username} (id={message.from_user.id})")

    await state.clear()  # ⛔️ Принудительно очищаем ВСЕ состояния
    await asyncio.sleep(0.1)  # 🔄 Даём FSM время сброситься

    await message.answer("Введите тему/контекст для генерации username:", reply_markup=back_to_main_kb())
    await state.set_state(GenerateUsernameStates.waiting_for_context)


### ✅ 3. ОБРАБОТЧИК ВВОДА КОНТЕКСТА
from keyboards.generate import styles_kb  # Импортируем клавиатуру с вариантами стилей

@generate_router.message(GenerateUsernameStates.waiting_for_context)
async def process_context_input(message: types.Message, bot: Bot, state: FSMContext):
    """
    Обработчик для введённого контекста. Проверяет его длину, затем предлагает выбрать стиль генерации.
    """
    context_text = message.text.strip()
    logging.info(f"📝 Введён контекст: '{context_text}' (от {message.from_user.username}, id={message.from_user.id})")

    # ✅ Проверяем длину контекста
    if len(context_text) > config.MAX_CONTEXT_LENGTH:
        logging.warning(f"⚠️ Контекст слишком длинный ({len(context_text)} символов), обрезаем до {config.MAX_CONTEXT_LENGTH}.")
        await message.answer(f"⚠️ Контекст слишком длинный. Обрезаю до {config.MAX_CONTEXT_LENGTH} символов.")
        context_text = context_text[:config.MAX_CONTEXT_LENGTH]

    # ✅ Сохраняем контекст в FSM, чтобы использовать после выбора стиля
    await state.update_data(context=context_text)

    # ✅ Отправляем inline-клавиатуру с выбором стиля
    await message.answer(
        "🎭 Выбери стиль, в котором будет сгенерировано имя:",
        reply_markup=styles_kb()  # Инлайн-кнопки со стилями
    )

    await state.set_state(GenerateUsernameStates.waiting_for_style)

@generate_router.callback_query(GenerateUsernameStates.waiting_for_style)
async def process_style_selection(query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обработчик выбора стиля: получает стиль, запускает генерацию username.
    """
    selected_style = query.data  # Получаем стиль из callback_data
    logging.info(f"🎭 Выбран стиль: {selected_style} (от {query.from_user.username}, id={query.from_user.id})")

    # ✅ Получаем сохранённый контекст из FSM
    data = await state.get_data()
    context_text = data.get("context", "")

    if not context_text:
        logging.error("⚠️ Ошибка: Контекст не найден в состоянии!")
        await query.message.answer("❌ Ошибка: не удалось получить тему генерации. Начните заново.", reply_markup=main_menu_kb())
        await state.clear()
        return

    # ✅ Отправляем сообщение о начале генерации
    waiting_message = await query.message.answer("⌛ Выслеживаю... Прислушиваюсь к цифровому эфиру...")

    try:
        logging.info(f"🚀 Запуск генерации username по контексту '{context_text}' и стилю '{selected_style}'")
        usernames = await asyncio.wait_for(
            get_available_usernames(bot, context_text, selected_style, config.AVAILABLE_USERNAME_COUNT),
            timeout=config.GEN_TIMEOUT
        )

    except asyncio.TimeoutError:
        logging.error(f"❌ Ошибка: Время ожидания генерации username истекло (контекст: '{context_text}', стиль: '{selected_style}').")
        await query.message.answer("⏳ Имялов искал имена слишком долго. Попробуйте позже.", reply_markup=main_menu_kb())
        await state.clear()
        return

    # ✅ Проверка на блокировку API
    if isinstance(usernames, str) and usernames.startswith("FLOOD_CONTROL"):
        retry_seconds = int(usernames.split(":")[1])
        logging.warning(f"🚨 Telegram API временно заблокировал бота на {retry_seconds} секунд.")
        await query.message.answer(f"🚫 Слишком частые запросы. Попробуйте снова через {retry_seconds // 60} минут.", reply_markup=main_menu_kb())
        await state.clear()
        return

    # ✅ Логируем результат
    if not usernames:
        logging.warning(f"❌ Генерация username не дала результатов (контекст: '{context_text}', стиль: '{selected_style}').")
        await query.message.answer("❌ Не удалось поймать имена. Возможно, тема слишком популярна. Попробуйте другой стиль!", reply_markup=error_retry_kb())
        return

    logging.info(f"✅ Сгенерировано {len(usernames)} username: {usernames}")

    # ✅ Отправляем результат
    kb_usernames = generate_username_kb(usernames)
    await query.message.answer(
        f"Вот три свободных имени в стиле *{selected_style}* на тему *{context_text}*:",
        parse_mode="MarkdownV2",
        reply_markup=kb_usernames
    )

    await state.clear()  # Очищаем состояние

