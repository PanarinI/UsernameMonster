import time
import traceback
import asyncio
import sys
import os
import logging
from setup import bot, dp
from handlers.start import start_router
from handlers.generate import generate_router
from handlers.check import check_router
from handlers.common import common_router
from handlers.help import help_router
from database.database import init_db
from utils.logger import setup_logging

# ✅ Настраиваем логирование
setup_logging()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# === 🔍 Переключаем режим работы на POLLING ===
IS_LOCAL = True  # ❗️ Принудительно включаем Polling

# === 🚀 Функция запуска бота ===
async def on_startup():
    """Запуск бота"""
    logging.info("🔗 Запускаем бота в режиме Polling")
    await init_db()

    # Подключаем обработчики команд
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(check_router)
    dp.include_router(generate_router)
    dp.include_router(common_router)

    await bot.delete_webhook()  # ❗ Отключаем Webhook перед Polling
    logging.info("🛑 Webhook отключён! Бот работает через Polling.")

# === 🚀 Основная логика ===
async def main():
    """Главная функция запуска"""
    await on_startup()
    await dp.start_polling(bot)  # ❗ Запускаем Polling

# === 🔥 Запуск ===
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())  # Запускаем бота в Polling

        # 🔥 Держим контейнер живым
        while True:
            logging.info("♻️ Контейнер работает, Amvera не убивай его!")
            time.sleep(30)

    except Exception as e:
        error_message = traceback.format_exc()
        logging.error(f"❌ Глобальная ошибка: {e}\n{error_message}")
