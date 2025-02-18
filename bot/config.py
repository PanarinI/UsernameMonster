import os
from dotenv import load_dotenv

load_dotenv()

## модель         gemini-flash-1.5-8b    gemini-flash-1.5   gpt-4o     gpt-4o-mini     deepseek-chat   deepseek-r1
MODEL = os.getenv("MODEL")
MAX_TOKENS = int(os.getenv("MAX_TOKENS"))
TEMPERATURE = float(os.getenv("TEMPERATURE"))

## генерация
PROMPT_NO_STYLE = (
    "Создай {n} уникальных и разнообразных username для Telegram по теме '{context}'.\n"
    "Только если тема явно указывает на бота, добавь 'bot' или '_bot'.\n"
    "Используй только латинские буквы, цифры и нижнее подчёркивание (не в начале и не в конце).\n"
    "Длина username: от 5 до 32 символов.\n"
    "Сначала укажи только одну категорию темы (например, 'бизнес'), затем  на следующей строке список username через запятую."
)

PROMPT_WITH_STYLE = (
    "Создай {n} уникальных и разнообразных username для Telegram по теме '{context}', учитывая стиль '{style}'.\n"
    "Только если тема явно указывает на бота, добавь 'bot' или '_bot'.\n"
    "Используй только латинские буквы, цифры и нижнее подчёркивание (не в начале и не в конце).\n"
    "Длина username: от 5 до 32 символов.\n"
    "Сначала укажи только одну категорию темы (например, 'бизнес'), затем  на следующей строке список username через запятую."
)

STYLE_DESCRIPTIONS = {
    "epic": "мощные, звучные, внушительные username, которые вызывают ощущение силы и значимости",
    "strict": "строгие, лаконичные, солидные username, которые выглядят профессионально",
    "funky": "игривые, необычные, креативные username с элементами юмора",
    "minimal": "простые, элегантные, короткие username, которые выглядят стильно",
    "cringe": "абсурдные, нелепые, запоминающиеся username, которые могут выглядеть смешно или странно"
}

STYLE_TRANSLATIONS = {
    "epic": "эпичный",
    "strict": "строгий",
    "funky": "фанк",
    "minimal": "минимализм",
    "cringe": "кринж"
}


# Максимальное количество символов в контексте
MAX_CONTEXT_LENGTH = 200

# Количество итоговых доступных username, которое должно возвращаться
AVAILABLE_USERNAME_COUNT = 3

# Количество username, запрашиваемых у OpenAI за один раз
GENERATED_USERNAME_COUNT = 5

# Максимальное количество итераций (попыток) генерации username
GEN_ATTEMPTS = int(os.getenv("GEN_ATTEMPTS"))

# Максимальное общее время ожидания генерации (в секундах)
GEN_TIMEOUT = int(os.getenv("GEN_TIMEOUT"))  # Преобразуем в число


# Прерывание после нескольких пустых ответов
MAX_EMPTY_RESPONSES = 3

# Параметр для интервала между запросами (например, 1 секунда) -- способ избежать flood control exceeded
REQUEST_INTERVAL = 0.3


# Логирование
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # Читаем переменную из окружения, если нет — ставим INFO
LOG_FILE = "bot.log"  # Оставьте пустым "", если хотите логи только в консоль
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

