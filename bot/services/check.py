import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
from config import REQUEST_INTERVAL
from database.database import save_username_to_db  # Импорт здесь, чтобы избежать циклических импортов

async def check_username_availability(username: str, save_to_db: bool = False) -> str:
    """Проверяет username и, если нужно, сохраняет в БД."""
    print(f"\n[STEP 1] 🔎 Начинаем проверку username: @{username}")

    result = await check_username_via_fragment(username)  # Проверяем через Fragment

    if save_to_db:
        await save_username_to_db(username=username, status=result, category="Пользовательская проверка", context="Ручная проверка", llm="none")

    return result


async def check_username_via_fragment(username: str) -> str:
    """Проверка статуса через Fragment. Анализирует редирект и 'Unavailable'."""
    url_username = f"https://fragment.com/username/{username}"
    url_query = f"https://fragment.com/?query={username}"

    print("[STEP 2] 🔹 Отправляем запрос к Fragment...")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url_username, ssl=ssl_context, allow_redirects=True) as response:
                final_url = str(response.url)
                # Если нас редиректит на ?query={username}, значит имя свободно (не 100%, но точнее не получается)
                if final_url == url_query:
                    print(f"[INFO] 🔹 Fragment сделал редирект на страницу поиска (Unavailable).")
                    return "Свободно"

                # Если остались на странице /username/{username}, значит нужно проверять статус
                html = await response.text()
                return await analyze_username_page(html, username)

    except aiohttp.ClientError as e:
        print(f"[ERROR] ❗ Ошибка при запросе к Fragment: {e}")
        return "Невозможно определить"


async def analyze_username_page(html: str, username: str) -> str:
    """Анализирует страницу конкретного юзернейма на Fragment."""
    soup = BeautifulSoup(html, 'html.parser')

    status_element = soup.find("span", class_="tm-section-header-status")
    if status_element:
        status_text = status_element.text.strip().lower()

        if "available" in status_text:
            print(f"[RESULT] ⚠️ Имя @{username} доступно для покупки.")
            return "Доступно для покупки"
        elif "sold" in status_text:
            print(f"[RESULT] ❌ Имя @{username} продано.")
            return "Продано"
        elif "taken" in status_text:
            print(f"[RESULT] ❌ Имя @{username} уже занято.")
            return "Занято"

    print(f"[WARNING] ⚠️ Статус Fragment (username) не определён.")
    return "Невозможно определить"
