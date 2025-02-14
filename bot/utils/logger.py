import logging
import os
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logging():
    handlers = [logging.StreamHandler()]  # Логируем в консоль (stdout) для Amvera

    # Если локальный запуск — пишем логи в файл
    if not os.getenv("AMVERA_ENV") and LOG_FILE:
        handlers.append(logging.FileHandler(LOG_FILE, mode="w"))

    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=handlers
    )

    logging.info("✅ Логирование настроено!")
