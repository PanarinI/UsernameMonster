import asyncio
import sys
import os
from setup import bot, dp
import logging
from handlers.start import start_router
from handlers.generate import generate_router
from handlers.check import check_router
from handlers.common import common_router
from handlers.help import help_router
from database.database import init_db


from utils.logger import setup_logging # Настройка логирования
setup_logging()  # Вызов перед запуском бота

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # для хостинга

async def main():
    """Запуск бота"""
    # Проверяем инициализацию БД
    await init_db()
    # Регистрируем обработчики
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(check_router)
    dp.include_router(generate_router)
    dp.include_router(common_router)

    logging.info("Бот запущен!")  # Логируем запуск
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())  # Асинхронный запуск


