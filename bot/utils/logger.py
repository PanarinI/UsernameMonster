import logging
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

# Функция для настройки логирования
def setup_logging():
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        filename=LOG_FILE if LOG_FILE else None,
        filemode="w" if LOG_FILE else None
    )



#### CHECK THIS TEST OUT. ЭТОТ ТЕКСТ ДОЛЖЕН ОСТАТСЯ
