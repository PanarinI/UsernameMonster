import time
import asyncio
import sys
import os
import logging
import json

from aiohttp import web
from setup import bot, dp
from aiogram.types import Update
from handlers.start import start_router
from handlers.generate import generate_router
from handlers.check import check_router
from handlers.help import help_router
from handlers.group import namehunt_command_router
from database.database import init_db
from logger import setup_logging

import config

# ✅ Настраиваем логирование
setup_logging()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# === 🔍 Определяем режим работы ===
IS_LOCAL = os.getenv("LOCAL_RUN", "false").lower() == "true"

# === 🌍 Настройки Webhook ===
WEBHOOK_HOST = os.getenv("WEBHOOK_URL", "https://namehuntbot-panarini.amvera.io").strip()
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}".replace("http://", "https://")

# === 🌐 Настройки Web-сервера ===
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("WEBHOOK_PORT", 80))

async def on_startup():
    """Запуск бота"""
    await init_db()

    # Подключаем обработчики команд
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(check_router)
    dp.include_router(generate_router)
    dp.include_router(namehunt_command_router)

    if IS_LOCAL:
        logging.info("🛑 Локальный запуск. Webhook НЕ будет установлен.")
        await bot.delete_webhook(drop_pending_updates=True)  # Очистим старые апдейты
    else:
        logging.info(f"🔗 Устанавливаем вебхук: {WEBHOOK_URL}")
        try:
            await bot.delete_webhook(drop_pending_updates=True)  # Очистим старые апдейты перед установкой вебхука
            await bot.set_webhook(WEBHOOK_URL)
            logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
        except Exception as e:
            logging.error(f"❌ Ошибка при установке Webhook: {e}")
            sys.exit(1)


async def on_shutdown(_):
    """Закрытие сессии перед остановкой"""
    logging.info("🚨 Бот остановлен! Закрываю сессию...")
    try:
        await bot.session.close()
    except Exception as e:
        logging.error(f"❌ Ошибка при закрытии сессии: {e}")
    logging.info("✅ Сессия закрыта.")




async def handle_update(request):
    """Обработчик Webhook (принимает входящие запросы от Telegram)"""
    time_start = time.time()
    raw_text = await request.text()

    try:
        update_data = json.loads(raw_text)
        current_time = int(time.time())

        # Фильтруем старые апдейты (старше 15 секунд)
        if "message" in update_data:
            message_time = update_data["message"]["date"]
            if current_time - message_time > 15:
                logging.warning(f"⚠️ Старая команда ({message_time}), игнорируем.")
                return web.Response(status=200)

        if "callback_query" in update_data:
            callback_time = update_data["callback_query"].get("date", current_time)
            if current_time - callback_time > 15:
                logging.warning(f"⚠️ Старая callback-команда ({callback_time}), игнорируем.")
                return web.Response(status=200)

        update = Update(**update_data)
        await dp.feed_update(bot=bot, update=update)

        time_end = time.time()
        logging.info(f"⏳ Обработка запроса заняла {time_end - time_start:.4f} секунд")
        return web.Response()

    except json.JSONDecodeError:
        logging.error(f"❌ Ошибка парсинга JSON: {raw_text}")

    except Exception as e:
        logging.error(f"❌ Ошибка обработки Webhook: {e}", exc_info=True)
        return web.Response(status=500)



async def handle_root(request):
    """Обработчик корневого запроса (проверка работы)"""
    logging.info("✅ Обработан GET-запрос на /")
    return web.Response(text="✅ Бот работает!", content_type="text/plain")


async def main():
    """Главная функция запуска"""
    await on_startup()

    if IS_LOCAL:
        logging.info("🚀 Запускаем бота в режиме Polling...")
        await dp.start_polling(bot)
        sys.exit(0)  # Прерываем выполнение, чтобы Webhook НЕ запускался!

    # 🌐 Если режим Webhook (сервер)
    logging.info("⚡ БОТ ПЕРЕЗАПУЩЕН (контейнер стартовал заново)")
    app = web.Application()
    app.add_routes([
        web.get("/", handle_root),
        web.post("/webhook", handle_update)
    ])
    app.on_shutdown.append(on_shutdown)
    return app


async def start_server():
    """Запуск сервера или Polling"""
    try:
        app = await main()

        if IS_LOCAL:
            logging.info("🚀 Запускаем бота в режиме Polling...")
            await dp.start_polling(bot)
            sys.exit(0)  # ⛔️ Прерываем выполнение, чтобы Webhook НЕ запускался!

        # 🌍 Webhook Mode
        logging.info("✅ Запускаем бота в режиме Webhook...")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", WEBAPP_PORT)
        await site.start()

        logging.info(f"✅ Webhook сервер запущен на порту {WEBAPP_PORT}")

        # ⏳ Ожидание завершения без `while True`
        await asyncio.Event().wait()

    except Exception as e:
        logging.error(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

logging.getLogger("asyncio").setLevel(logging.WARNING)  # ✅ Отключает DEBUG для asyncio


if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logging.info("🛑 Бот остановлен пользователем.")
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}")

    while True:
        time.sleep(3600)  # ⬅️ Держим процесс живым
