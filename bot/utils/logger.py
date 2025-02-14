import logging
import os
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logging():
    # Создаём кастомный обработчик, который всегда пишет в stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # Очищаем все предыдущие обработчики (иначе может быть дублирование)
    root_logger = logging.getLogger()
    root_logger.handlers = []  # 💡 Удаляем старые обработчики
    root_logger.setLevel(LOG_LEVEL)
    root_logger.addHandler(console_handler)

    # Логируем в файл, только если запущено ЛОКАЛЬНО
    if LOG_FILE and not os.getenv("AMVERA_ENV"):
        file_handler = logging.FileHandler(LOG_FILE, mode="w")
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger.addHandler(file_handler)

    logging.info("✅ Логирование настроено!")
    print("✅ Логирование настроено!")  # Print остаётся, чтобы убедиться
