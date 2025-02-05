import openai
from aiogram import Bot
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
from services.check import check_username_availability
from handlers.check import is_valid_username
import config
from config import setup_logging

load_dotenv()
setup_logging()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Создаём клиент OpenAI
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

async def generate_usernames(context: str, n: int = 5) -> list[str]:
    """
    Генерирует список username на основе контекста.
    """
    prompt = (
        f"Придумай {n} username для Telegram по контексту: '{context}'.\n"
        "Если из контекста ясно, что username нужен для телеграм-бота, то прибавляй к концу bot или _bot"
        "Используй только латинские буквы, цифры и нижнее подчёркивание. "
        "Длина username должна быть от 5 до 32 символов. Выведи их в виде списка через запятую."
    )

    # Запрос к модели OpenAI
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
    )

    # Логируем ответ API перед обработкой
    logging.debug(f"API Response: {response}")

    # Проверяем, есть ли нужное поле в ответе
    if response.choices and response.choices[0].message and response.choices[0].message.content:
        usernames_raw = response.choices[0].message.content.strip()
    else:
        logging.warning("Ответ от API не содержит ожидаемых данных.")
        usernames_raw = ""

    # Парсим ответ
    usernames_raw = response.choices[0].message.content.strip()
    usernames = [u.strip() for u in usernames_raw.split(",")]

    # Фильтруем корректные username
    return [username for username in usernames if is_valid_username(username)]

async def get_available_usernames(bot: Bot, context: str, n: int = 3) -> list[str]:
    """
    Гарантированно возвращает ровно `n` доступных username.
    """
    available_usernames = set()

    while len(available_usernames) < n:
        usernames = await generate_usernames(context, n=5)  # Запрашиваем 5 username
        for username in usernames:
            if username in available_usernames:
                continue
            result = await check_username_availability(bot, username)
            if result == "Свободно":
                available_usernames.add(username)
                if len(available_usernames) >= n:
                    break

    return list(available_usernames)
