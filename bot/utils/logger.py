import logging
import os
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logging():
    handlers = [logging.StreamHandler()]  # 📌 Всегда пишем в stdout (для Amvera)

    # Логируем в файл, только если запущено ЛОКАЛЬНО
    if LOG_FILE and not os.getenv("AMVERA_ENV"):
        handlers.append(logging.FileHandler(LOG_FILE, mode="w"))

    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=handlers
    )

    logging.info("✅ Логирование настроено!")
    print("✅ Логирование настроено!")  # Отдельный print для проверки
