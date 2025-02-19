import time
import logging
from aiogram import Bot, types
from aiogram.fsm.context import FSMContext

async def measure_username_generation(
    bot: Bot,
    message: types.Message,
    state: FSMContext,
    context: str,
    style: str | None,
    n: int
):
    """
    Обертка для измерения времени выполнения генерации username
    и отправки ответа пользователю.
    """

    logging.info(f"🚀 Запуск генерации username по контексту '{context}' и стилю '{style}'")

    # 1️⃣ Замер общего времени обработки события
    event_start = time.time()

    # Отправка начального сообщения
    send_start = time.time()
    await message.answer("⌛ Генерирую...")
    send_duration = time.time() - send_start
    logging.info(f"⏳ Время отправки сообщения о начале генерации: {send_duration:.2f} сек")

    # ✅ Ленивый импорт, чтобы избежать циклического импорта
    from services.generate import get_available_usernames

    # 2️⃣ Замер времени генерации username (бизнес-логика)
    gen_start = time.time()
    usernames = await get_available_usernames(bot, context, style, n)
    gen_duration = time.time() - gen_start
    logging.info(f"⏳ Время генерации username: {gen_duration:.2f} сек")

    # 3️⃣ Замер времени отправки результата пользователю
    send_start = time.time()
    await message.answer(f"✅ Сгенерировано {len(usernames)} username: {usernames}")
    send_duration = time.time() - send_start
    logging.info(f"⏳ Время отправки результата в Telegram: {send_duration:.2f} сек")

    # 4️⃣ Замер времени очистки состояния
    clear_start = time.time()
    await state.clear()  # Очистка состояния FSM
    clear_duration = time.time() - clear_start
    logging.info(f"⏳ Время очистки состояния: {clear_duration:.2f} сек")

    # ✅ Общее время обработки события
    total_duration = time.time() - event_start
    logging.info(f"🕒 Полное время обработки события: {total_duration:.2f} сек")
