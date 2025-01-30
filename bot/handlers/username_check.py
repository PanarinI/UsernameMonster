from aiogram import Bot, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
import re
import aiohttp
import ssl

# Определяем состояния FSM
class UsernameCheck(StatesGroup):
    waiting_for_username = State()

async def handle_check_command(message: Message, state: FSMContext):
    """Обрабатывает команду /check и переводит в состояние ожидания username"""
    await message.reply("🔍 Введите username, который хотите проверить:")
    await state.set_state(UsernameCheck.waiting_for_username)

async def handle_username_input(message: Message, bot: Bot, state: FSMContext):
    """Обрабатывает введённый username"""
    username = message.text.strip().replace("@", "")

    # Проверяем формат username
    if not re.match(r"^[a-zA-Z0-9_]{5,32}$", username) or "__" in username or username.startswith("_") or username.endswith("_"):
        await message.reply(
            "❌ Ошибка: username должен соответствовать следующим требованиям:\n"
            "✅ Латинские буквы, цифры и `_`\n"
            "✅ Длина: 5-32 символа\n"
            "✅ Не начинаться и не заканчиваться `_`\n"
            "✅ Не содержать два подряд `_`"
        )
        return

    # Проверяем доступность username
    status = await check_username_availability(bot, username)

    # Отправляем результат пользователю
    responses = {
        "Свободно": f"✅ Имя @{username} свободно!",
        "Занято": f"❌ Имя @{username} уже занято.",
        "Невозможно определить": f"⚠️ Не удалось определить доступность имени @{username}. Попробуйте позже."
    }
    await message.reply(responses[status])

    # Сбрасываем состояние
    await state.clear()

async def check_username_availability(bot: Bot, username: str) -> str:
    """Проверяет, свободен ли юзернейм в Telegram через API и t.me."""
    print(f"\n[STEP 1] 🔎 Начинаем проверку username: @{username}")

    try:
        print("[STEP 2] 🔹 Отправляем запрос в Telegram API...")
        await bot.get_chat(f"@{username}")  # Пробуем получить чат
        print(f"[RESULT] ❌ Имя @{username} занято (найдено через API).")
        return "Занято"

    except TelegramBadRequest as e:
        error_message = str(e).lower()
        print(f"[INFO] ❗ Ошибка API: {error_message}")

        if "chat not found" in error_message:
            print(f"[STEP 3] 🔹 Имя @{username} не найдено в API. Переходим к проверке через t.me...")
            return await check_username_via_web(username)

        print(f"[ERROR] ❗ Неожиданная ошибка API: {error_message}")
        return "Невозможно определить"

async def check_username_via_web(username: str) -> str:
    """Дополнительная проверка через t.me/{username} с анализом HTML-кода."""
    url = f"https://t.me/{username}"
    print("[STEP 4] 🔹 Отправляем запрос к t.me...")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=ssl_context) as response:
            text = await response.text()

            if response.status == 404:
                print(f"[RESULT] ✅ Имя @{username} свободно (проверено через t.me)")
                return "Свободно"

            title_match = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE)
            title_text = title_match.group(1) if title_match else ""

            if "tgme_page_title" in text or "If you have Telegram, you can contact" in text:
                print(f"[RESULT] ❌ Имя @{username} занято (проверено через t.me)")
                return "Занято"

            if f"Telegram: Contact @{username}" in title_text and "tgme_page_title" not in text:
                print(f"[RESULT] ✅ Имя @{username} свободно (по заголовку, но без признаков профиля)")
                return "Свободно"

            print(f"[WARNING] ⚠️ Непонятный ответ от t.me для @{username}: {response.status}, HTML: {text[:500]}")
            return "Невозможно определить"
