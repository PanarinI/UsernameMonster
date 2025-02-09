import asyncio
import re
import aiohttp
import os
import certifi
import ssl
from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
# from config import BOT_TOKEN




# Устанавливаем переменную окружения для SSL
os.environ["SSL_CERT_FILE"] = certifi.where()

print(f"[SETUP] SSL_CERT_FILE установлен в: {os.environ['SSL_CERT_FILE']}")

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


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


@dp.message(F.text.startswith("/check"))
async def check(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Использование: /check [username]")
        return

    username = args[1].replace("@", "")

    # 🔹 Проверяем, соответствует ли username критериям Telegram
    if not re.match(r"^[a-zA-Z0-9_]{5,32}$", username) or "__" in username or username.startswith(
            "_") or username.endswith("_"):
        await message.reply(
            "❌ Ошибка: username должен соответствовать следующим требованиям:\n"
            "1️⃣ **Содержать только латинские буквы (`A-Z, a-z`), цифры (`0-9`) и `_`**\n"
            "2️⃣ **Быть длиной от 5 до 32 символов**\n"
            "3️⃣ **Не начинаться и не заканчиваться `_`**\n"
            "4️⃣ **Не содержать два подряд идущих `_` (например, `hello__world`)**"
        )
        return

    status = await check_username_availability(username)

    responses = {
        "Свободно": f"✅ Имя @{username} свободно!",
        "Занято": f"❌ Имя @{username} уже занято.",
        "Невозможно определить": f"⚠️ Не удалось определить доступность имени @{username}. Попробуйте позже."
    }

    print(f"[FINAL RESULT] 📢 Итог для @{username}: {status}\n" + "-" * 50)
    await message.reply(responses[status])


async def main():
    """Запуск бота"""
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
