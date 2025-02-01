import logging

# Настройки логирования
logging.basicConfig(
    level=logging.INFO,  # INFO = логируем всё важное, ERROR = только ошибки
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    filename="bot.log",  # Лог записывается в этот файл
    filemode="a"  # "a" = дописывать в файл, "w" = каждый раз перезаписывать
)

# Функция логирования
def log_action(action: str):
    logging.info(action)
