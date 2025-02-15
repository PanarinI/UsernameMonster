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

# ✅ Добавляем путь к корневой директории (нужно для корректного импорта)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# === 1️⃣ Определяем режим работы ===
IS_LOCAL = os.getenv("LOCAL_RUN", "false").lower() == "true"  # LOCAL_RUN=true → Polling

# === 2️⃣ Настройки Webhook ===
WEBHOOK_HOST = os.getenv("WEBHOOK_URL", "https://namehuntbot-panarini.amvera.io").strip() # Домен Amvera
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}".replace("http://", "https://")  # Принудительно HTTPS, полный URL вебхука

# === 3️⃣ Настройки Web-сервера ===
WEBAPP_HOST = "0.0.0.0"  # Запускаем сервер на всех интерфейсах
WEBAPP_PORT = int(os.getenv("WEBHOOK_PORT", 80))  # Берём порт из WEBHOOK_PORT


# === 4️⃣ Функции старта и остановки ===
async def on_startup():
    """Запуск бота"""
    print(f"🔗 Устанавливаем вебхук: {WEBHOOK_URL}")
    await init_db()  # Инициализация базы данных

    # ✅ Подключаем все обработчики команд
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(check_router)
    dp.include_router(generate_router)
    dp.include_router(common_router)

    if IS_LOCAL: # если запускаем локально
        await bot.delete_webhook()  # ❗ Отключаем Webhook перед Polling
        logging.info("🛑 Webhook отключён! Бот работает через Polling.")
    else: # если запускаем с облака
        try:
            await bot.delete_webhook()  # ❗ Удаляем старый Webhook перед установкой нового
            logging.info(f"🔍 Webhook Host: {WEBHOOK_HOST}")
            logging.info(f"🔍 Webhook Path: {WEBHOOK_PATH}")
            print(f"🔍 Устанавливаем Webhook по адресу: {WEBHOOK_URL}")  # Отладочный вывод
            logging.info(f"📌 Webhook URL перед установкой: {WEBHOOK_URL}")
            if not WEBHOOK_URL.startswith("https://"):
                logging.error("❌ Ошибка: Webhook URL должен начинаться с HTTPS!")

            await bot.set_webhook(WEBHOOK_URL)  # 🔗 Устанавливаем Webhook
            logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
        except Exception as e:
            logging.error(f"❌ Ошибка при установке Webhook: {e}")

async def on_shutdown(_):
    """Остановка бота"""
    logging.info("🚨 Бот остановлен! Закрываю сессию...")
    try:
        await bot.session.close()  # Закрываем HTTP-сессию
    except Exception as e:
        logging.error(f"❌ Ошибка при закрытии сессии: {e}")
    logging.info("✅ Сессия закрыта.")


async def handle_update(request):
    """Обработчик Webhook (принимает входящие запросы от Telegram)"""
    logging.info(f"📩 Получен запрос от Telegram: {await request.text()}")  # Логируем весь запрос
    update = await request.json()  # Получаем JSON
    await dp.feed_update(bot=bot, update=update)  # Передаём в aiogram
    return web.Response()  # Отправляем OK


async def handle_root(request):
    logging.info("✅ Обработан GET-запрос на /")
    print("✅ Обработан GET-запрос на /")  # Чтобы точно увидеть в логах
    return web.Response(text="✅ Бот работает!", content_type="text/plain")

async def log_all_requests(app, handler):
    async def middleware_handler(request):
        logging.info(f"📥 Входящий запрос: {request.method} {request.path}")
        print(f"📥 Входящий запрос: {request.method} {request.path}")
        return await handler(request)
    return middleware_handler

app = web.Application(middlewares=[log_all_requests])



# === 5️⃣ Основная логика бота ===
async def main():
    """Главная функция запуска"""
    await on_startup()  # Выполняем стартовые настройки

    if IS_LOCAL:
        # 🔄 Polling (локальный режим)
        await dp.start_polling(bot)
    else:
        # 🌐 Webhook (серверный режим)
        app = web.Application()
        app.add_routes([
            web.get("/", handle_root),
            web.head("/", handle_root),  # Добавляем HEAD-запросы
        ])
        app.router.add_post("/webhook", handle_update)  # ✅ Фиксированный путь
        app.on_shutdown.append(on_shutdown)  # Добавляем обработчик остановки
        logging.info("✅ Зарегистрированные маршруты в приложении:")
        for route in app.router.routes():
            try:
                logging.info(f"➡️ {route.method} {route.path}")
            except AttributeError:
                logging.info(f"⚠️ Пропущен маршрут: {route}")
        return app

import socket

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("0.0.0.0", port)) == 0

port_status = "Открыт" if check_port(WEBAPP_PORT) else "❌ Закрыт"
print(f"🔎 Проверка порта {WEBAPP_PORT}: {port_status}")
logging.info(f"🔎 Проверка порта {WEBAPP_PORT}: {port_status}")


# === 6️⃣ Запуск ===
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        app = loop.run_until_complete(main())  # Запускаем бота

        if not IS_LOCAL:
            print(f"🚀 Попытка запустить сервер на {WEBAPP_HOST}:{WEBAPP_PORT}")
            logging.info(f"🚀 Попытка запустить сервер на {WEBAPP_HOST}:{WEBAPP_PORT}")
            web.run_app(app, host="0.0.0.0", port=80, access_log=logging)

        # 🔥 Держим контейнер живым
        while True:
            print("♻️ Контейнер работает, Amvera не убивай его!")
            time.sleep(30)

    except Exception as e:
        error_message = traceback.format_exc()
        logging.error(f"❌ Глобальная ошибка: {e}\n{error_message}")
