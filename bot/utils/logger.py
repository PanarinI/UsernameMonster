import logging
import os
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logging():
    """Настраивает логирование в зависимости от среды (локально или облако)."""
    IS_LOCAL = os.getenv("LOCAL_RUN", "false").lower() == "true"

    # Создаём корневой логгер
    root_logger = logging.getLogger()
    root_logger.handlers = []  # Убираем старые обработчики, если были
    root_logger.setLevel(LOG_LEVEL)

    # 🖥️ Логирование в консоль (только если в облаке)
    if not IS_LOCAL:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger.addHandler(console_handler)

    # 📄 Логирование в файл (только если локально)
    if IS_LOCAL and LOG_FILE:
        file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")  # <-- Добавил encoding="utf-8"
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger.addHandler(file_handler)

    logging.info("✅ Логирование настроено!")
