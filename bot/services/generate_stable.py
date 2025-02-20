from aiogram import Bot
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging

import config
from services.check import check_username_availability  # Проверка username
from handlers.check import is_valid_username  # Валидация username

# Загрузка переменных окружения и настройка логирования
load_dotenv()
#setup_logging()

# Получение ключей API из окружения
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Создание клиента OpenAI для генерации username
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

async def generate_username_list(context: str, n: int = config.GENERATED_USERNAME_COUNT) -> list[str]:
    """
    Генерирует `n` username на основе контекста.
    """
    logging.info(f"🔄 Генерация username: context='{context}', n={n}")

    prompt = config.PROMPT.format(n=n, context=context)

    # Запрос к AI API
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
    )

    logging.debug(f"API Response: {response}")

    # Если API вернул данные, извлекаем username
    if response.choices and response.choices[0].message and response.choices[0].message.content:
        usernames_raw = response.choices[0].message.content.strip()
    else:
        logging.warning("⚠️ API не вернул username.")
        return []

    # Парсинг ответа: разделяем строку по запятым и фильтруем валидные username
    usernames = [u.strip() for u in usernames_raw.split(",")]
    valid_usernames = [username for username in usernames if is_valid_username(username)]

    return valid_usernames

async def gen_process_and_check(bot: Bot, context: str, n: int = config.AVAILABLE_USERNAME_COUNT) -> list[str]:
    """
    Возвращает `n` доступных username, избегая повторных проверок.
    """
    logging.info(f"🔎 Поиск {n} доступных username для контекста: '{context}'")

    available_usernames = set()
    checked_usernames = set()  # Список уже проверенных username
    attempts = 0  # Количество попыток генерации
    empty_responses = 0  # Количество пустых ответов AI

    while len(available_usernames) < n and attempts < config.GEN_ATTEMPTS:
        attempts += 1
        logging.info(f"🔄 Попытка {attempts}/{config.GEN_ATTEMPTS}")

        # Генерация username
        usernames = await generate_username_list(context, n=config.GENERATED_USERNAME_COUNT)
        logging.debug(f"📜 Сгенерированные username: {usernames}")

        # Если API не вернул username
        if not usernames:
            empty_responses += 1
            logging.warning(f"⚠️ AI не дал username ({empty_responses}/{config.MAX_EMPTY_RESPONSES})")

            # Прерывание после нескольких пустых ответов
            if empty_responses >= config.MAX_EMPTY_RESPONSES:
                logging.error("❌ AI отказывается генерировать username. Останавливаем процесс.")
                break

            continue

        for username in usernames:
            # Пропуск уже проверенных username
            if username in checked_usernames:
                continue

            # Добавляем в список проверенных
            checked_usernames.add(username)

            # Проверка доступности
            result = await check_username_availability(bot, username)
            logging.debug(f"🔍 Проверка username '{username}': {result}")

            if result == "Свободно":
                available_usernames.add(username)

            # Достаточно доступных username
            if len(available_usernames) >= n:
                break

    logging.info(f"✅ Итоговые доступные username: {available_usernames}")
    return list(available_usernames)

