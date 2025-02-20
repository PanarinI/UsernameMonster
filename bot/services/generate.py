from aiogram import Bot
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
import asyncio
from typing import List
import re

from database.database import save_username_to_db
from services.check import check_multiple_usernames  # Проверка username
from handlers.check import is_valid_username   # Валидация username

import config


# Загрузка переменных окружения и настройка логирования
load_dotenv()

# Получение ключей API из окружения
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Создание клиента OpenAI для генерации username
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)



REJECTION_PATTERNS = [
    r"не могу",
    r"противоречит",
    r"извините",
    r"это запрещено",
    r"не допускается"
]

def is_rejection_response(usernames: List[str]) -> bool:
    """
    Проверяет, содержит ли список username текстовый отказ от AI.
    """
    for username in usernames:
        # Проверяем, есть ли кириллица (признак текста, а не username)
        if re.search(r'[а-яА-Я]', username):
            # Проверяем на наличие шаблонов отказа
            if any(re.search(pattern, username.lower()) for pattern in REJECTION_PATTERNS):
                return True
    return False


async def generate_username_list(context: str, style: str | None, n: int = config.GENERATED_USERNAME_COUNT) -> tuple[list[str], str]:
    """
    Генерирует `n` username на основе контекста и стиля (если стиль указан).
    Возвращает список username (или текст отказа) и категорию.
    """
    logging.info(f"🔄 Генерация username: context='{context}', style='{style}', n={n}")

    if style:
        prompt = config.PROMPT_WITH_STYLE.format(n=n, context=context, style=style)
        prompt_type = "WITH STYLE"
    else:
        prompt = config.PROMPT_NO_STYLE.format(n=n, context=context)
        prompt_type = "NO STYLE"

    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
    )

    logging.debug(f"API Response: {response}")

    if response.choices and response.choices[0].message and response.choices[0].message.content:
        response_text = response.choices[0].message.content.strip()
        logging.info(f"📝 Полный ответ AI: {response_text}")

        lines = [line.strip() for line in response_text.split("\n") if line.strip()]

        if len(lines) < 2:
            logging.warning("⚠️ API не вернул категорию, берем 'Неизвестно'")
            category = "Неизвестно"
            usernames_raw = lines[0] if lines else ""
        else:
            category = lines[0].replace("Категория:", "").strip()
            usernames_raw = lines[1]

        raw_usernames = [u.strip() for u in usernames_raw.split(",")]

        # Проверка на текстовый отказ по этическим соображениям
        if is_rejection_response(raw_usernames):
            logging.warning("❌ AI вернул текст отказа по этическим соображениям.")
            return raw_usernames, "Этический отказ"

        # Фильтрация только валидных username
        valid_usernames = [username for username in raw_usernames if is_valid_username(username)]
        logging.info(f"✅ категория: {category}, сгенерировано username: {len(valid_usernames)}")

        return valid_usernames, category

    else:
        logging.warning("⚠️ API не вернул корректные данные.")
        return [], "Неизвестно"



async def gen_process_and_check(bot: Bot, context: str, style: str | None, n: int = config.AVAILABLE_USERNAME_COUNT) -> list[str]:
    logging.info(f"🔎 Поиск {n} доступных username для контекста: '{context}' со стилем: '{style}'")

    available_usernames = set()
    checked_usernames = set()
    attempts = 0
    empty_responses = 0

    while len(available_usernames) < n and attempts < config.GEN_ATTEMPTS:
        attempts += 1
        logging.info(f"🔄 Попытка {attempts}/{config.GEN_ATTEMPTS}")

        try:
            usernames, category = await generate_username_list(context, style or "", n=config.GENERATED_USERNAME_COUNT)
        except Exception as e:
            logging.error(f"❌ Ошибка генерации username через OpenAI: {e}")
            return []

        if is_rejection_response(usernames):
            logging.warning("❌ AI вернул текст отказа по этическим соображениям.")
            # ✅ Немедленно возвращаем пустой результат, чтобы остановить дальнейшие попытки
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

            tasks.append(
                save_username_to_db(username=username, status=result, category=category, context=context, style=style, llm=config.MODEL)
            )

        if tasks:
            try:
                await asyncio.gather(*tasks)
            except Exception as e:
                logging.error(f"❌ Ошибка при записи в БД: {e}")

    logging.info(f"✅ Итоговые доступные username: {available_usernames}")
    return list(available_usernames)
