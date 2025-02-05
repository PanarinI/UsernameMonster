import openai
from aiogram import Bot
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
from services.check import check_username_availability # Импорт функции проверки (инкапсулирует два этапа)
from handlers.check import is_valid_username # Функция для валидации формата username
import config
from config import setup_logging

# Загрузка переменных окружения и настройка логирования
load_dotenv()
setup_logging()

# Получение ключей API из окружения
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Создание клиента OpenAI для отправки запросов к API
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

async def generate_usernames(context: str, n: int = config.GENERATED_USERNAME_COUNT) -> list[str]:
    """
    Генерирует список username на основе контекста.
    """
    logging.info(f"Генерация username: context='{context}', n={n}")

    prompt = config.PROMPT.format(n=n, context=context)

    # Запрос к модели OpenAI
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
    )

    logging.debug(f"API Response: {response}")

    # Если в ответе присутствует нужное поле, извлекаем сгенерированные username
    if response.choices and response.choices[0].message and response.choices[0].message.content: #  если в ответе есть текст с username
        usernames_raw = response.choices[0].message.content.strip() # извлекаем его
    else:
        logging.warning("Ответ от API не содержит ожидаемых данных.")
        return []

    # Парсинг ответа: разделяем строку по запятым и удаляем лишние пробелы
    usernames = [u.strip() for u in usernames_raw.split(",")]

    # Фильтрация – оставляем только те username, которые соответствуют требованиям валидации
    return [username for username in usernames if is_valid_username(username)]

async def get_available_usernames(bot: Bot, context: str, n: int = config.AVAILABLE_USERNAME_COUNT) -> list[str]:
    """
    Возвращает `n` доступных username.
    """
    logging.info(f"Поиск {n} доступных username для контекста: '{context}'")

    # Множество для хранения уникальных доступных username
    available_usernames = set()

    # Пока не набрано нужное количество доступных username
    while len(available_usernames) < n:
        # Генерируем n вариантов username по заданному контексту
        usernames = await generate_usernames(context, n=config.GENERATED_USERNAME_COUNT)
        logging.debug(f"Сгенерированные username: {usernames}")
        # Если генерация не вернула ни одного варианта – выходим
        if not usernames:
            logging.error("API не вернул username. Останавливаем повторные запросы.")
            return []

        for username in usernames:
            # Если данный username уже добавлен, пропускаем его
            if username in available_usernames:
                continue
            # Вызываем функцию проверки доступности
            result = await check_username_availability(bot, username)
            logging.debug(f"Проверка username '{username}': {result}")

            # Если результат проверки равен "Свободно", добавляем его в итоговое множество
            if result == "Свободно":
                available_usernames.add(username)
                if len(available_usernames) >= n:
                    break

    logging.info(f"Итоговые доступные username: {available_usernames}")
    return list(available_usernames)
