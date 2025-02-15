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

async def generate_usernames(context: str, n: int = config.GENERATED_USERNAME_COUNT) -> tuple[list[str], str]:
    """
    Генерирует `n` username и определяет категорию.
    """
    logging.info(f"📝 Генерация username: context='{context}', n={n}")

    prompt = config.PROMPT.format(n=n, context=context)

    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=config.MAX_TOKENS,
        temperature=config.TEMPERATURE,
    )

    logging.debug(f"API Response: {response}")

    # Получаем usage-данные (токены)
    input_tokens = response.usage.prompt_tokens if response.usage else 0
    output_tokens = response.usage.completion_tokens if response.usage else 0
    total_tokens = response.usage.total_tokens if response.usage else 0

    if response.choices and response.choices[0].message and response.choices[0].message.content:
        response_text = response.choices[0].message.content.strip()
        lines = [line.strip() for line in response_text.split("\n") if line.strip()]

        if len(lines) < 2:  # Если OpenAI не вернул категорию
            logging.warning("⚠️ API не вернул категорию, берем 'Неизвестно'")
            category = "Неизвестно"
            usernames_raw = lines[0] if lines else ""  # Если OpenAI вообще ничего не вернул
        else:
            category = lines[0]
            usernames_raw = lines[1]

        usernames = [u.strip() for u in usernames_raw.split(",")]

        # Фильтрация username
        valid_usernames = [username for username in usernames if is_valid_username(username)]

        # Гарантия, что список содержит только строки
        valid_usernames = [str(u) for u in valid_usernames]

        logging.debug(f"✅ Итоговая категория: {category}")
        logging.debug(f"✅ Итоговые username: {valid_usernames} ({type(valid_usernames)})")

        # === Вывод отчета в консоль ===
        print("\n========== ОТЧЕТ ПО ГЕНЕРАЦИИ ==========")
        print(f"📌 Контекст запроса: {context}")
        print(f"📌 Полный ответ модели:\n{response_text}")
        print(f"📌 Категория: {category}")
        print(f"📌 Сгенерированные username: {valid_usernames}")
        print(f"📌 Токены: input={input_tokens}, output={output_tokens}, всего={total_tokens}")
        print("========================================\n")

        if not valid_usernames:
            logging.warning("⚠️ Ошибка: Все username оказались недействительными.")
            return [], category

        return valid_usernames, category

    else:
        logging.warning("⚠️ API не вернул корректные данные.")
        return [], "Неизвестно"


async def get_available_usernames(bot: Bot, context: str, n: int = config.AVAILABLE_USERNAME_COUNT) -> list[str] | str:
    """
    Возвращает `n` доступных username по контексту
    Генерирует и проверяет имена по мере необходимости.
    """
    logging.info(f"🔎 Поиск {n} доступных username для контекста: '{context}'")

    available_usernames = set()
    checked_usernames = set()  # Уже проверенные username
    attempts = 0  # Счетчик попыток генерации
    empty_responses = 0  # Количество пустых ответов AI

    while len(available_usernames) < n and attempts < config.GEN_ATTEMPTS:
        attempts += 1
        logging.info(f"🔄 Попытка {attempts}/{config.GEN_ATTEMPTS}")

        # Генерация username и category
        try:
            usernames, category = await generate_usernames(context, n=config.GENERATED_USERNAME_COUNT)
        except Exception as e:
            logging.error(f"❌ Ошибка генерации username через OpenAI: {e}")
            return []  # Ошибка в API AI - прерываем генерацию

        if not usernames:
            empty_responses += 1
            logging.warning(f"⚠️ AI не дал username ({empty_responses}/{config.MAX_EMPTY_RESPONSES})")

            if empty_responses >= config.MAX_EMPTY_RESPONSES:
                logging.error("❌ AI отказывается генерировать username. Останавливаем процесс.")
                break

            continue # Попытка генерации нового списка

        for username in usernames:
            if username in checked_usernames:
                continue  # Пропускаем уже проверенные

            checked_usernames.add(username)

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

            await save_username_to_db(username=username, status=result, category=category, context=context, llm=config.MODEL)

            if len(available_usernames) >= n:
                break  # Выходим из цикла, если набрали нужное количество

            # Если все имена уже проверены и не хватает доступных, генерируем новый список
        if len(available_usernames) < n:
            logging.info("🔄 Генерация новых имен, так как не хватает доступных.")

    if not available_usernames:
        logging.warning("⚠️ Не найдено доступных username.")

    return list(available_usernames)

