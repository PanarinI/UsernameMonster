import aiohttp
import asyncio

async def check_tme(username):
    url = f"https://t.me/{username}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False) as response:
            text = await response.text()
            print(f"\n🔎 Проверяем t.me/{username}")
            print(f"🛠 HTTP Status: {response.status}")
            print(f"📜 HTML Response: {text[:1000]}")  # Выводим первые 1000 символов HTML

async def main():
    usernames = ["macron", "zybakul", "yandex", "pukin"]
    await asyncio.gather(*(check_tme(username) for username in usernames))

asyncio.run(main())












import aiohttp
import re
import ssl
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

async def check_username_availability(username: str) -> str:
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

    try:
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

    except aiohttp.ClientError as e:
        # Обработка ошибок сети при выполнении запроса к t.me
        print(f"[ERROR] ❗ Ошибка при запросе к t.me: {e}")
        return "Невозможно определить"
