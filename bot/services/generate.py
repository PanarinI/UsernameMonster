from aiogram import Bot
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
import config
from services.check import check_username_availability  # Проверка username
from handlers.check import is_valid_username  # Валидация username
from database.database import save_username_to_db
from aiogram.exceptions import TelegramRetryAfter

# Загрузка переменных окружения и настройка логирования
load_dotenv()

# Получение ключей API из окружения
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Создание клиента OpenAI для генерации username
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

async def generate_usernames(context: str, style: str | None, n: int) -> tuple[list[str], str]:
    """
    Генерирует `n` username в указанном стиле (или без стиля) и определяет категорию.
    """
    logging.info(f"📝 Генерация username: context='{context}', style='{style}', n={n}")

    # ✅ Выбираем нужный промпт
    if style:
        prompt = config.PROMPT_WITH_STYLE.format(n=n, context=context, style=style)
    else:
        prompt = config.PROMPT_NO_STYLE.format(n=n, context=context)

    logging.info(f"📜 Используемый PROMPT:\n{prompt}")

    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
    )

    logging.debug(f"API Response: {response}")

    # ✅ Разбираем ответ модели
    if response.choices and response.choices[0].message and response.choices[0].message.content:
        response_text = response.choices[0].message.content.strip()
        lines = [line.strip() for line in response_text.split("\n") if line.strip()]

        if len(lines) < 2:  # Если OpenAI не вернул категорию
            logging.warning("⚠️ API не вернул категорию, берем 'Неизвестно'")
            category = "Неизвестно"
            usernames_raw = lines[0] if lines else ""  # Если OpenAI вообще ничего не вернул
        else:
            # ✅ Убираем "Категория:" из первой строки
            category = lines[0].replace("Категория:", "").strip()
            usernames_raw = lines[1]  # Вторая строка — список username

        usernames = [u.strip() for u in usernames_raw.split(",")]

        logging.info(f"✅ Итоговая категория: {category}")
        logging.info(f"✅ Итоговые username: {usernames}")

        return usernames, category

    else:
        logging.warning("⚠️ API не вернул корректные данные.")
        return [], "Неизвестно"


async def get_available_usernames(bot: Bot, context: str, style: str | None, n: int):
    """Запрашивает у модели генерацию username с учётом стиля."""

    # ✅ Принудительно приводим n к int, если вдруг пришла строка
    try:
        n = int(n)
    except ValueError:
        logging.error(f"❌ Ошибка: n должно быть числом, но пришло {type(n)} ({n})")
        n = config.AVAILABLE_USERNAME_COUNT  # Используем значение по умолчанию

    available_usernames = set()  # Используем set, чтобы избежать дубликатов
    checked_usernames = set()  # Добавляем объявление переменной!
    attempts = 0
    empty_responses = 0  # Добавляем счётчик пустых ответов

    while len(available_usernames) < n and attempts < config.GEN_ATTEMPTS:
        attempts += 1
        logging.info(f"🔄 Попытка {attempts}/{config.GEN_ATTEMPTS}")

        # Генерация username и category
        try:
            usernames, category = await generate_usernames(context, style or "", n)  # ✅ Исправлено, чтобы `None` → `""`
        except Exception as e:
            logging.error(f"❌ Ошибка генерации username через OpenAI: {e}")
            return []  # Ошибка в API AI - прерываем генерацию

        if not usernames:
            empty_responses += 1
            logging.warning(f"⚠️ AI не дал username ({empty_responses}/{config.MAX_EMPTY_RESPONSES})")

            if empty_responses >= config.MAX_EMPTY_RESPONSES:
                logging.error("❌ AI отказывается генерировать username. Останавливаем процесс.")
                break

            continue  # Попытка генерации нового списка

        for username in usernames:
            if username in checked_usernames:
                continue  # Пропускаем уже проверенные

            checked_usernames.add(username)

            # ✅ ДОБАВЛЯЕМ ПРОВЕРКУ НА ВАЛИДНОСТЬ username
            if not is_valid_username(username):
                continue  # Пропускаем невалидные username

            try:
                result = await check_username_availability(username)

                # 🛑 Если поймали `FLOOD_CONTROL`, сразу возвращаем его, чтобы бот остановился
                if result.startswith("FLOOD_CONTROL"):
                    logging.error(f"🚫 Flood Control! Остановка с сообщением: {result}")
                    return result

            except Exception as e:
                logging.error(f"❌ Ошибка при проверке {username}: {e}")
                continue  # Ошибка на сервере Fragment или бота - просто пропускаем

            logging.debug(f"🔍 Проверка username '{username}': {result}")

            if result == "Свободно":
                available_usernames.add(username)

            await save_username_to_db(username=username, status=result, category=category, context=context, style=style, llm=config.MODEL)

            if len(available_usernames) >= n:
                break  # Выходим из цикла, если набрали нужное количество

        # Если все имена уже проверены и не хватает доступных, генерируем новый список
        if len(available_usernames) < n:
            logging.info("🔄 Генерация новых имен, так как не хватает доступных.")

    if not available_usernames:
        logging.warning("⚠️ Не найдено доступных username.")

    return list(available_usernames)
