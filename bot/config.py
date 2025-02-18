## модель         gemini-flash-1.5-8b    gemini-flash-1.5   gpt-4o     gpt-4o-mini     deepseek-chat   deepseek-r1
MODEL = "gemini-flash-1.5"
MAX_TOKENS = 40
TEMPERATURE = 0.75

## генерация
PROMPT = (
    "Создай {n} уникальных разнообразных username для Telegram по теме '{context}' в стиле '{style}'.\n"
    "Если тема явно про бота, добавь 'bot' или '_bot'.\n"
    "Только латинские буквы, цифры, нижнее подчеркивание (не в начале и не в конце).\n"
    "Длина: 5-32 символа.\n"
    "Сначала укажи категорию (напр. 'бизнес'), затем список username через запятую."
)

STYLE_DESCRIPTIONS = {
    "epic": "мощные, звучные, внушительные username, которые вызывают ощущение силы и значимости",
    "strict": "строгие, лаконичные, солидные username, которые выглядят профессионально",
    "funky": "игривые, необычные, креативные username с элементами юмора",
    "minimal": "простые, элегантные, короткие username, которые выглядят стильно",
    "cringe": "абсурдные, нелепые, запоминающиеся username, которые могут выглядеть смешно или странно"
}




# Максимальное количество символов в контексте
MAX_CONTEXT_LENGTH = 200

# Количество итоговых доступных username, которое должно возвращаться
AVAILABLE_USERNAME_COUNT = 3

# Количество username, запрашиваемых у OpenAI за один раз
GENERATED_USERNAME_COUNT = 5

# Максимальное количество итераций (попыток) генерации username
GEN_ATTEMPTS = 5

# Максимальное общее время ожидания генерации (в секундах)
GEN_TIMEOUT = 25

# Прерывание после нескольких пустых ответов
MAX_EMPTY_RESPONSES = 3

# Параметр для интервала между запросами (например, 1 секунда) -- способ избежать flood control exceeded
REQUEST_INTERVAL = 0.3

##Логирование
LOG_LEVEL = "DEBUG"  # Можно менять на DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "bot.log"  # Оставьте пустым "", если хотите логи только в консоль
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


