import time
import traceback
import socket
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
from utils.logger import setup_logging

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

# === 🔎 Функция проверки доступности порта ===
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("0.0.0.0", port)) == 0

# === 🚀 Функция запуска бота ===
async def on_startup():
    """Запуск бота"""
    logging.info(f"🔗 Устанавливаем вебхук: {WEBHOOK_URL}")
    await init_db()

    # Подключаем обработчики команд
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(check_router)
    dp.include_router(generate_router)
    dp.include_router(common_router)

    if IS_LOCAL:
        await bot.delete_webhook()
        logging.info("🛑 Webhook отключён! Бот работает через Polling.")
    else:
        try:
            await bot.delete_webhook()
            logging.info(f"🔍 Webhook Host: {WEBHOOK_HOST}")
            logging.info(f"🔍 Webhook Path: {WEBHOOK_PATH}")
            logging.info(f"📌 Webhook URL перед установкой: {WEBHOOK_URL}")

            if not WEBHOOK_URL.startswith("https://"):
                logging.error("❌ Ошибка: Webhook URL должен начинаться с HTTPS!")

            await bot.set_webhook(WEBHOOK_URL)
            logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
        except Exception as e:
            logging.error(f"❌ Ошибка при установке Webhook: {e}")
            sys.exit(1)  # Прерываем запуск

# === 🛑 Функция остановки бота ===
async def on_shutdown(_):
    logging.info("🚨 Бот остановлен! Закрываю сессию...")
    try:
        await bot.session.close()
    except Exception as e:
        logging.error(f"❌ Ошибка при закрытии сессии: {e}")
    logging.info("✅ Сессия закрыта.")

# === 📩 Обработчик Webhook ===
async def handle_update(request):
    """Обработчик Webhook (принимает входящие запросы от Telegram)"""
    time_start = time.time()

    try:
        update_data = await request.json()

        if "callback_query" in update_data:
            callback = update_data["callback_query"]
            user = callback["from"]
            message = callback.get("message", {})

            clean_log = (
                f"📩 Callback: {callback['data']}\n"
                f"👤 От: {user.get('first_name', 'Неизвестный')} (@{user.get('username', 'Нет юзернейма')})\n"
                f"💬 Сообщение: {message.get('text', 'Без текста')}"
            )
            logging.info(clean_log)

        update = Update(**update_data)
        await dp.feed_update(bot=bot, update=update)

        time_end = time.time()
        logging.info(f"⏳ Обработка запроса заняла {time_end - time_start:.4f} секунд")
        return web.Response()

    except Exception as e:
        logging.error(f"❌ Ошибка обработки Webhook: {e}", exc_info=True)
        return web.Response(status=500)


async def handle_root(request):
    logging.info("✅ Обработан GET-запрос на /")
    return web.Response(text="✅ Бот работает!", content_type="text/plain")

# === 🚀 Основная логика ===
async def main():
    """Главная функция запуска"""
    await on_startup()

    if IS_LOCAL:
        await dp.start_polling(bot)
    else:
        app = web.Application()
        app.add_routes([
            web.get("/", handle_root),
            web.post("/webhook", handle_update)
        ])
        app.on_shutdown.append(on_shutdown)
        return app

# === 🔥 Функция старта сервера ===
async def start_server():
    try:
        app = await main()
        if IS_LOCAL:
            return  # Локальный запуск → Polling

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", WEBAPP_PORT)
        await site.start()

        logging.info("✅ Сервер запущен через AppRunner")
        print("✅ Сервер запущен через AppRunner")

        # 🔎 Проверяем, что порт 80 реально открыт
        if is_port_in_use(WEBAPP_PORT):
            logging.info(f"🟢 Порт {WEBAPP_PORT} успешно открыт и слушает входящие запросы.")
        else:
            logging.error(f"❌ Порт {WEBAPP_PORT} НЕ открыт! Возможно, Amvera его не видит.")

        # 🔥 Держим контейнер живым
        while True:
            logging.info("♻️ Контейнер активен. Проверка раз в 30 секунд.")
            await asyncio.sleep(30)
    except Exception as e:
        logging.error(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)

# === 🚀 Запуск сервера ===
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(start_server())
