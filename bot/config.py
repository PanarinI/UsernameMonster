## модель         gemini-flash-1.5-8b    gemini-flash-1.5   gpt-4o     gpt-4o-mini     deepseek-chat   deepseek-r1
MODEL = "gemini-flash-1.5"
MAX_TOKENS = 40
TEMPERATURE = 0.75

## генерация
PROMPT = (
    "Придумай {n} уникальных и разнообразных username для Telegram по следующей тематике: '{context}'.\n"
    "Когда в контексте прямо указано, что нужно придумать username для бота, то добавляй к концу username 'bot' или '_bot'"
    "Используй только латинские буквы, цифры и нижнее подчёркивание. Нижнее подчеркивание запрещено в начале и в конце username"
    "Длина username должна быть от 5 до 32 символов"
    "Сначала укажи обобщенную категорию тематики в одной строке (напр. 'бизнес'), затем выведи список {n} username через запятую."
)

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
REQUEST_INTERVAL = 0.5

##Логирование
LOG_LEVEL = "DEBUG"  # Можно менять на DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "bot.log"  # Оставьте пустым "", если хотите логи только в консоль
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


