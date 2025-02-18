import time
import asyncio
import sys
import os
import logging
from aiohttp import web
from setup import bot, dp
from aiogram.types import Update
from handlers.start import start_router
from handlers.generate import generate_router
from handlers.check import check_router
from handlers.common import common_router
from handlers.help import help_router
from database.database import init_db
from logger import setup_logging

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
    logging.info("🚀 Запуск бота...")

    try:
        await bot.delete_webhook(drop_pending_updates=True)  # 🔥 Очищаем старые запросы при запуске
        logging.info("🛑 Webhook отключён! Очередь обновлений очищена.")
    except Exception as e:
        logging.warning(f"⚠️ Не удалось удалить Webhook: {e}")

    # Устанавливаем Webhook в облаке
    if not IS_LOCAL:
        logging.info("🌍 Облачный режим: БД будет использоваться через Webhook.")
        try:
            await bot.set_webhook(WEBHOOK_URL)
            logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
        except Exception as e:
            logging.error(f"❌ Ошибка при установке Webhook: {e}")
            sys.exit(1)  # Прерываем запуск, если вебхук не установился


    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(check_router)
    dp.include_router(generate_router)
    dp.include_router(common_router)

    if IS_LOCAL:
        logging.info("🟢 Локальный режим: запускаем Polling.")
        return

    # Устанавливаем Webhook в облаке
    try:
        if not WEBHOOK_URL.startswith("https://"):
            logging.error("❌ Ошибка: Webhook URL должен начинаться с HTTPS!")
            return

        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
    except Exception as e:
        logging.error(f"❌ Ошибка при установке Webhook: {e}")
        sys.exit(1)  # Прерываем запуск, если вебхук не установился



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
    logging.info(f"📩 Получен запрос от Telegram: {await request.text()}")
    time_start = time.time()

    try:
        update_data = await request.json()

        # 🔥 Проверяем дату сообщения или callback-запроса
        current_time = int(time.time())

        if "message" in update_data and "date" in update_data["message"]:
            message_time = update_data["message"]["date"]
            if current_time - message_time > 5:  # Если сообщение старше 5 секунд — игнорируем
                logging.warning(f"⚠️ Старый message, игнорируем: {message_time}")
                return web.Response(status=200)

        if "callback_query" in update_data and "id" in update_data["callback_query"]:
            callback_time = update_data["callback_query"]["message"]["date"]
            if current_time - callback_time > 5:  # Если callback старше 5 секунд — игнорируем
                logging.warning(f"⚠️ Старый callback_query, игнорируем: {callback_time}")
                return web.Response(status=200)

        update = Update(**update_data)
        await dp.feed_update(bot=bot, update=update)

        time_end = time.time()
        logging.info(f"⏳ Обработка запроса заняла {time_end - time_start:.4f} секунд")
        return web.Response()
    except Exception as e:
        logging.error(f"❌ Ошибка обработки Webhook: {e}")
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
        await dp.start_polling(bot)  # 🚀 Гарантируем, что Polling запустится!
        return  # ⬅️ Без return код дальше не идёт и не завершает процесс

    # 🌐 Если режим Webhook
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
            while True:
                await asyncio.sleep(360)  # ⬅️ Держим процесс живым в Polling!
            return

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", WEBAPP_PORT)
        await site.start()

        logging.info("✅ Сервер запущен через Webhook")

        while True:
            await asyncio.sleep(360)  # ⬅️ Держим сервер живым

    except Exception as e:
        logging.error(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

logging.getLogger("asyncio").setLevel(logging.WARNING)  # ✅ Отключает DEBUG для asyncio

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logging.info("🛑 Бот остановлен пользователем.")
