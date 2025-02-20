from aiogram import Bot
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
import asyncio

from database.database import save_username_to_db
import config
from services.check import check_multiple_usernames  # Проверка username
from handlers.check import is_valid_username  # Валидация username

# Загрузка переменных окружения и настройка логирования
load_dotenv()


# Получение ключей API из окружения
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Создание клиента OpenAI для генерации username
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

async def generate_username_list(context: str, style: str | None, n: int = config.GENERATED_USERNAME_COUNT) -> tuple[list[str], str]:
    """
    Генерирует `n` username на основе контекста и стиля (если стиль указан).
    Возвращает список валидных username и категорию.
    """
    logging.info(f"🔄 Генерация username: context='{context}', style='{style}', n={n}")

    # Выбор нужного промпта в зависимости от наличия стиля
    if style:
        prompt = config.PROMPT_WITH_STYLE.format(n=n, context=context, style=style)
        prompt_type = "WITH STYLE"
    else:
        prompt = config.PROMPT_NO_STYLE.format(n=n, context=context)
        prompt_type = "NO STYLE"

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
        response_text = response.choices[0].message.content.strip()
        lines = [line.strip() for line in response_text.split("\n") if line.strip()]

        if len(lines) < 2:
            logging.warning("⚠️ API не вернул категорию, берем 'Неизвестно'")
            category = "Неизвестно"
            usernames_raw = lines[0] if lines else ""
        else:
            category = lines[0].replace("Категория:", "").strip()
            usernames_raw = lines[1]

        usernames = [u.strip() for u in usernames_raw.split(",")]

        # ✅ Фильтрация только валидных username
        valid_usernames = [username for username in usernames if is_valid_username(username)]
        logging.info(f"✅ категория: {category}, сгенерировано username: {len(valid_usernames)}")

        return valid_usernames, category

    else:
        logging.warning("⚠️ API не вернул корректные данные.")
        return [], "Неизвестно"


async def gen_process_and_check(bot: Bot, context: str, style: str | None, n: int = config.AVAILABLE_USERNAME_COUNT) -> list[str]:
    """
    Возвращает `n` доступных username, избегая повторных проверок.
    """
    logging.info(f"🔎 Поиск {n} доступных username для контекста: '{context}' со стилем: '{style}'")

    available_usernames = set()
    checked_usernames = set()  # Список уже проверенных username
    attempts = 0  # Количество попыток генерации
    empty_responses = 0  # Количество пустых ответов AI

    while len(available_usernames) < n and attempts < config.GEN_ATTEMPTS:
        attempts += 1
        logging.info(f"🔄 Попытка {attempts}/{config.GEN_ATTEMPTS}")

        try:
            usernames, category = await generate_username_list(context, style or "", n=config.GENERATED_USERNAME_COUNT)
        except Exception as e:
            logging.error(f"❌ Ошибка генерации username через OpenAI: {e}")
            return []

        if not usernames:
            empty_responses += 1
            logging.warning(f"⚠️ AI не дал username ({empty_responses}/{config.MAX_EMPTY_RESPONSES})")

            if empty_responses >= config.MAX_EMPTY_RESPONSES:
                logging.error("❌ AI отказывается генерировать username. Останавливаем процесс.")
                break

            continue


        valid_usernames = [u for u in usernames if u not in checked_usernames and is_valid_username(u)]
        checked_usernames.update(valid_usernames)

        if not valid_usernames:
            continue

        try:
            check_results = await check_multiple_usernames(valid_usernames)
        except Exception as e:
            logging.error(f"❌ Ошибка при проверке username: {e}")
            continue

        tasks = []
        for username, result in check_results.items():
            if result == "Свободно" and len(available_usernames) < n:
                available_usernames.add(username)

            # Добавление задачи для записи в БД
            tasks.append(
                save_username_to_db(username=username, status=result, category=category, context=context, style=style, llm=config.MODEL)
            )

        # Асинхронная запись в БД
        if tasks:
            try:
                await asyncio.gather(*tasks)
            except Exception as e:
                logging.error(f"❌ Ошибка при записи в БД: {e}")

    logging.info(f"✅ Итоговые доступные username: {available_usernames}")
    return list(available_usernames)

