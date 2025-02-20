import logging
import asyncio
import re
from datetime import datetime
from typing import List
from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from services.generate import gen_process_and_check
from keyboards.generate import generate_username_kb, error_retry_kb, styles_kb, initial_styles_kb
from keyboards.main_menu import main_menu_kb, back_to_main_kb
from .states import GenerateUsernameStates

import config


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
    await state.update_data(start_time=datetime.now().isoformat())
    await query.message.answer(
        "🔮 О чём должно говорить имя? Опиши тему, и я поймаю три уникальных имени.\n"
        "📖 <i>Например: «загадки истории», «фиолетовые котики», да что угодно</i>",
        parse_mode="HTML",
        reply_markup=back_to_main_kb()
    )

    await state.set_state(GenerateUsernameStates.waiting_for_context)
    await query.answer()  # Telegram требует подтверждения, что callback обработан.


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


@generate_router.message(GenerateUsernameStates.waiting_for_context)
async def process_context_input(message: types.Message, state: FSMContext):
    """
    Обработчик для введённого контекста. Теперь после ввода темы появляется 2 варианта:
    - Без выбора стиля (генерация сразу)
    - Выбрать стиль (открывает второе меню)
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

    # ✅ Отправляем inline-клавиатуру с двумя вариантами
    await message.answer(
        "🎭 Как будем искать имя?",
        reply_markup=initial_styles_kb()  # Меню первого уровня
    )

    await state.set_state(GenerateUsernameStates.waiting_for_style)


@generate_router.callback_query(GenerateUsernameStates.waiting_for_style)
async def process_style_choice(query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обрабатывает выбор стиля или генерацию без стиля.
    """
    selected_option = query.data

    if selected_option == "choose_style":
        # ✅ Если пользователь выбирает "Выбрать стиль", показываем меню стилей
        await query.message.edit_text(
            "🎭 Выбери стиль генерации:",
            reply_markup=styles_kb()
        )
        return  # ⛔️ Завершаем функцию, чтобы не вызывать генерацию

    elif selected_option == "no_style":
        # ✅ Если выбран "без стиля", сразу запускаем генерацию
        await state.update_data(start_time=datetime.now().isoformat())
        progress_task = asyncio.create_task(send_progress_messages(query))
        await perform_username_generation(query, state, bot, style=None)
        progress_task.cancel()
        return

    # ✅ Если выбран конкретный стиль, запускаем генерацию с указанным стилем
    await state.update_data(start_time=datetime.now().isoformat())
    progress_task = asyncio.create_task(send_progress_messages(query))
    await perform_username_generation(query, state, bot, style=selected_option)
    progress_task.cancel()


def contains_cyrillic(text: str) -> bool:
    """Проверяет, есть ли в тексте кириллические символы."""
    return bool(re.search(r'[а-яА-Я]', text))


def escape_md(text: str) -> str:
    """Экранирует спецсимволы для MarkdownV2"""
    if not text:
        return ""
    return re.sub(r'([_*[\]()~`>#+-=|{}.!])', r'\\\1', text)



async def send_progress_messages(query: types.CallbackQuery):
    """Фоновая отправка сообщений о процессе генерации."""
    messages = [
        "Выслеживаю...",
        "Прислушиваюсь к цифровому эфиру...",
        "...",
    ]

    sent_messages = []
    for msg in messages:
        try:
            sent_messages.append(await query.message.answer(msg))
            await asyncio.sleep(5)  # Задержка перед следующим сообщением
        except Exception as e:
            logging.error(f"❌ Ошибка при отправке сообщения о процессе генерации: {e}")
            break

    return sent_messages


async def perform_username_generation(query: types.CallbackQuery, state: FSMContext, bot: Bot, style: str | None):
    data = await state.get_data()
    context_text = data.get("context", "")
    start_time = data.get("start_time", "")

    if not start_time:
        logging.warning("⚠️ Внимание! start_time не найден в FSM. Установим текущее время.")
        start_time = datetime.now().isoformat()

    if not context_text:
        await query.message.answer("❌ Ошибка: не удалось получить тему генерации. Начните заново.", reply_markup=main_menu_kb())
        await state.clear()
        return

    logging.info(f"🚀 Генерация username: контекст='{context_text}', стиль='{style}'")

    try:
        raw_usernames = await asyncio.wait_for(
            gen_process_and_check(bot, context_text, style, config.AVAILABLE_USERNAME_COUNT),
            timeout=config.GEN_TIMEOUT
        )
        usernames = [u.strip() for u in raw_usernames if u.strip()]

        if not usernames:
            logging.warning(f"❌ AI отказался генерировать username по этическим соображениям (контекст: '{context_text}', стиль: '{style}').")
            await query.message.answer(
                "❌ AI отказался генерировать имена по этическим соображениям. Попробуйте изменить запрос.",
                reply_markup=error_retry_kb()
            )
            await state.clear()
            return

        await handle_generation_result(query, usernames, context_text, style, start_time)
        await state.clear()

    except Exception as e:
        logging.error(f"❌ Ошибка генерации: {e}")
        await query.message.answer("❌ Ошибка при генерации. Попробуйте ещё раз.", reply_markup=error_retry_kb())
        await state.clear()




async def handle_generation_result(query: types.CallbackQuery, usernames: list[str], context: str, style: str | None,
                                   start_time: str):
    """
    Отправка результата генерации username пользователю.
    """
    # Безопасное преобразование времени генерации
    try:
        start_dt = datetime.fromisoformat(start_time)
    except ValueError:
        logging.error(f"❌ Ошибка: Некорректный формат start_time: '{start_time}'. Используем текущее время.")
        start_dt = datetime.now()

    # Вычисляем время генерации
    duration = (datetime.now() - start_dt).total_seconds()

    style_rus = config.STYLE_TRANSLATIONS.get(style, style or "")
    time_prefix = f"[{escape_md(f'{duration:.2f}')} сек] "  # Экранируем время с точкой
    text = f"{time_prefix}Вот уникальные имена {'в стиле *' + escape_md(style_rus) + '*' if style else ''} на тему *{escape_md(context)}*:"

    await query.message.answer(
        text,
        parse_mode="MarkdownV2",
        reply_markup=generate_username_kb(usernames)
    )
    logging.info("✅ Результаты генерации отправлены пользователю.")
