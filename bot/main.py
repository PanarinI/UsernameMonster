import time
import traceback
import socket
import asyncio
import sys
import os
import logging
from aiohttp import web
from setup import bot, dp
from handlers.start import start_router
from handlers.generate import generate_router
from handlers.check import check_router
from handlers.common import common_router
from handlers.help import help_router
from database.database import init_db
from utils.logger import setup_logging  # Логирование

setup_logging()  # Запуск логирования

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

IS_LOCAL = os.getenv("LOCAL_RUN", "false").lower() == "true"

WEBHOOK_HOST = os.getenv("WEBHOOK_URL", "https://namehuntbot-panarini.amvera.io").strip()
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}".replace("http://", "https://")

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("WEBHOOK_PORT", 80))


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("0.0.0.0", port)) == 0


if is_port_in_use(WEBAPP_PORT):
    logging.error(f"❌ Порт {WEBAPP_PORT} уже используется другим процессом!")
    sys.exit(1)


async def on_startup():
    print(f"🔗 Устанавливаем вебхук: {WEBHOOK_URL}")
    await init_db()

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
            print(f"🔍 Устанавливаем Webhook по адресу: {WEBHOOK_URL}")
            logging.info(f"📌 Webhook URL перед установкой: {WEBHOOK_URL}")

            if not WEBHOOK_URL.startswith("https://"):
                logging.error("❌ Ошибка: Webhook URL должен начинаться с HTTPS!")

            await bot.set_webhook(WEBHOOK_URL)
            logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
        except Exception as e:
            logging.error(f"❌ Ошибка при установке Webhook: {e}")
            print(f"❌ Ошибка при установке Webhook: {e}")
            sys.exit(1)


async def on_shutdown(_):
    logging.info("🚨 Бот остановлен! Закрываю сессию...")
    try:
        await bot.session.close()
    except Exception as e:
        logging.error(f"❌ Ошибка при закрытии сессии: {e}")
    logging.info("✅ Сессия закрыта.")


async def handle_update(request):
    logging.info(f"📩 Получен запрос от Telegram: {await request.text()}")
    update = await request.json()
    await dp.feed_update(bot=bot, update=update)
    return web.Response()


async def handle_root(request):
    logging.info("✅ Обработан GET-запрос на /")
    return web.Response(text="✅ Бот работает!", content_type="text/plain")


async def log_all_requests(app, handler):
    async def middleware_handler(request):
        logging.info(f"📥 Входящий запрос: {request.method} {request.path}")
        return await handler(request)

    return middleware_handler


async def main():
    await on_startup()

    if IS_LOCAL:
        await dp.start_polling(bot)
    else:
        app = web.Application(middlewares=[log_all_requests])
        app.add_routes([
            web.get("/", handle_root),
            web.post("/webhook", handle_update)
        ])
        app.on_shutdown.append(on_shutdown)
        return app


async def start_server():
    try:
        app = await main()

        if IS_LOCAL:
            return

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", WEBAPP_PORT)
        await site.start()
        logging.info("✅ Сервер запущен через AppRunner")
        print("✅ Сервер запущен через AppRunner")

        if is_port_in_use(WEBAPP_PORT):
            logging.info(f"🟢 Порт {WEBAPP_PORT} успешно открыт и слушает входящие запросы.")
            print(f"🟢 Порт {WEBAPP_PORT} успешно открыт и слушает входящие запросы.")
        else:
            logging.error(f"❌ Порт {WEBAPP_PORT} НЕ открыт! Возможно, Amvera его не видит.")
            print(f"❌ Порт {WEBAPP_PORT} НЕ открыт! Возможно, Amvera его не видит.")

        # 💡 Фикс: Держим контейнер живым
        while True:
            await asyncio.sleep(30)

    except Exception as e:
        logging.error(f"❌ Ошибка запуска сервера: {e}")
        print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)


async def handle_exception(loop, context):
    logging.error(f"❌ Глобальная ошибка в asyncio: {context['message']}")
    print(f"❌ Глобальная ошибка в asyncio: {context['message']}")
    sys.exit(1)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.set_exception_handler(handle_exception)

loop.run_until_complete(start_server())
