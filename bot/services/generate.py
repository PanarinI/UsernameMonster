import os
import time
import logging
from dotenv import load_dotenv
import asyncio
from aiogram import Bot
from openai import OpenAI

from services.check import check_multiple_usernames  # Проверка username
from handlers.check import is_valid_username  # Валидация username
from database.database import save_username_to_db

import config


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

    # ✅ Чистый лог запроса без текста промпта
    logging.debug(
        f"📡 Запрос к API: "
        f"model={config.MODEL}, "
        f"max_tokens={config.MAX_TOKENS}, "
        f"temperature={config.TEMPERATURE}, "
        f"prompt_type={prompt_type}"
    )

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
    """Запрашивает у модели генерацию username с учётом стиля и проверяет их уникальность."""

    try:
        n = int(n)
    except ValueError:
        logging.error(f"❌ Ошибка: n должно быть числом, но пришло {type(n)} ({n})")
        n = config.AVAILABLE_USERNAME_COUNT

    start_time = time.time()
    attempts = 0
    available_usernames = set()
    checked_usernames = set()
    total_checked = 0
    total_free = 0
    empty_responses = 0

    while len(available_usernames) < n and attempts < config.GEN_ATTEMPTS:
        attempts += 1
        logging.info(f"🔄 Попытка {attempts}/{config.GEN_ATTEMPTS}")

        try:
            usernames, category = await generate_usernames(context, style or "", n)
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

        response_text = " ".join(usernames).lower()
        logging.info(f"🔍 AI сгенерировал: {usernames}")

        if any(phrase in response_text for phrase in ["не могу", "противоречит", "извините", "это запрещено", "не допускается"]):
            logging.warning("❌ AI отказался генерировать. Прерываем генерацию!")
            break

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
            total_checked += 1
            if result == "Свободно" and len(available_usernames) < n:  # ✅ Проверка лимита!
                total_free += 1
                available_usernames.add(username)

            tasks.append(
                save_username_to_db(username=username, status=result, category=category, context=context, style=style, llm=config.MODEL)
            )

        if tasks:
            try:
                await asyncio.gather(*tasks)
            except Exception as e:
                logging.error(f"❌ Ошибка при записи в БД: {e}")

        if len(available_usernames) >= n:
            break

    duration = time.time() - start_time
    logging.info(f"📊 Итог генерации: {attempts} попыток, {total_checked} проверено, {total_free} свободных, {len(available_usernames)} выдано. ⏳ {duration:.2f} сек.")

    # ✅ Ограничиваем результат до n username
    return list(available_usernames)[:n]
