import aiohttp
import re
import ssl
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

async def check_username_availability(bot: Bot, username: str) -> str:
    """Проверяет, свободен ли юзернейм в Telegram через API и t.me."""
    print(f"\n[STEP 1] 🔎 Проверяем username: @{username}")

    try:
        print("[STEP 2] 🔹 Запрос в Telegram API...")
        # Первый этап: запрос к Telegram API с использованием метода get_chat
        await bot.get_chat(f"@{username}")  # Если чат существует → username занят
        print(f"[RESULT] ❌ Имя @{username} занято (API).")
        return "Занято"

    except TelegramBadRequest as e:
        # Если возникает ошибка, преобразуем сообщение в нижний регистр для проверки
        error_message = str(e).lower()
        print(f"[INFO] ❗ Ошибка API: {error_message}")

        # Если ошибка содержит "chat not found", значит чат не найден → переходим ко второму этапу проверки
        if "chat not found" in error_message:
            print(f"[STEP 3] 🔹 Имя @{username} не найдено в API. Проверяем через t.me...")
            return await check_username_via_web(username)

        # Если ошибка иная – возвращаем статус "Невозможно определить"
        print(f"[ERROR] ❗ Неожиданная ошибка API: {error_message}")
        return "Невозможно определить"

async def check_username_via_web(username: str) -> str:
    """Дополнительная проверка через t.me/{username} с анализом HTML-кода."""
    url = f"https://t.me/{username}"
    print("[STEP 4] 🔹 Запрос к t.me...")

    # Создаём SSL-контекст для безопасного подключения (ssl отключён для тестирования)
    ssl_context = ssl.create_default_context()

    async with aiohttp.ClientSession() as session:
        try:
            # Выполняем GET-запрос к странице t.me/{username}
            async with session.get(url, ssl=False) as response:
                text = await response.text()
                # Если получен статус 404 – страница не найдена, значит username свободен
                if response.status == 404:
                    print(f"[RESULT] ✅ Имя @{username} свободно (t.me).")
                    return "Свободно"
                # Ищем заголовок страницы для дополнительного анализа
                title_match = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE)
                title_text = title_match.group(1) if title_match else ""
                # Если в HTML содержится 'tgme_page_title' или фраза "If you have Telegram, you can contact" – username занят
                if "tgme_page_title" in text or "If you have Telegram, you can contact" in text:
                    print(f"[RESULT] ❌ Имя @{username} занято (t.me).")
                    return "Занято"
                # Если в заголовке обнаружено "Telegram: Contact @username" и при этом отсутствует 'tgme_page_title' в тексте – username свободен
                if f"Telegram: Contact @{username}" in title_text and "tgme_page_title" not in text:
                    print(f"[RESULT] ✅ Имя @{username} свободно (по заголовку).")
                    return "Свободно"
                # Если ни одно из условий не выполнено – возвращаем статус "Невозможно определить"
                print(f"[WARNING] ⚠️ Странный ответ t.me для @{username}: {response.status}, HTML: {text[:500]}")
                return "Невозможно определить"

        except aiohttp.ClientError as e:
            # Обработка ошибок сети при выполнении запроса к t.me
            print(f"[ERROR] ❗ Ошибка при запросе к t.me: {e}")
            return "Невозможно определить"