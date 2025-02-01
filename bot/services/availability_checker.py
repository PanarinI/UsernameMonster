import aiohttp
import ssl
import re
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

async def check_username_availability(bot: Bot, username: str) -> str:
    """Проверяет, свободен ли юзернейм в Telegram через API и t.me."""
    print(f"\n[STEP 1] 🔎 Проверяем username: @{username}")

    try:
        print("[STEP 2] 🔹 Запрос в Telegram API...")
        await bot.get_chat(f"@{username}")  # Если чат существует → username занят
        print(f"[RESULT] ❌ Имя @{username} занято (API).")
        return "Занято"

    except TelegramBadRequest as e:
        error_message = str(e).lower()
        print(f"[INFO] ❗ Ошибка API: {error_message}")

        if "chat not found" in error_message:
            print(f"[STEP 3] 🔹 Имя @{username} не найдено в API. Проверяем через t.me...")
            return await check_username_via_web(username)

        print(f"[ERROR] ❗ Неожиданная ошибка API: {error_message}")
        return "Невозможно определить"

async def check_username_via_web(username: str) -> str:
    """Дополнительная проверка через t.me/{username} с анализом HTML-кода."""
    url = f"https://t.me/{username}"
    print("[STEP 4] 🔹 Запрос к t.me...")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=ssl_context) as response:
            text = await response.text()

            if response.status == 404:
                print(f"[RESULT] ✅ Имя @{username} свободно (t.me).")
                return "Свободно"

            title_match = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE)
            title_text = title_match.group(1) if title_match else ""

            if "tgme_page_title" in text or "If you have Telegram, you can contact" in text:
                print(f"[RESULT] ❌ Имя @{username} занято (t.me).")
                return "Занято"

            if f"Telegram: Contact @{username}" in title_text and "tgme_page_title" not in text:
                print(f"[RESULT] ✅ Имя @{username} свободно (по заголовку).")
                return "Свободно"

            print(f"[WARNING] ⚠️ Странный ответ t.me для @{username}: {response.status}, HTML: {text[:500]}")
            return "Невозможно определить"
