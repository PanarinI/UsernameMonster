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
WEBHOOK_HOST = os.getenv("WEBHOOK_URL", "https://namehuntbot-panarini.amvera.io")  # Домен Amvera
WEBHOOK_PATH = f"/bot/{os.getenv('BOT_TOKEN')}"  # Путь вебхука
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"  # Полный URL вебхука

# === 3️⃣ Настройки Web-сервера ===
WEBAPP_HOST = "0.0.0.0"  # Запускаем сервер на всех интерфейсах
WEBAPP_PORT = int(os.getenv("PORT", 8080))  # Порт из окружения (должен быть 443 на сервере)

# === 4️⃣ Функции старта и остановки ===
async def on_startup():
    """Запуск бота"""
    await init_db()  # Инициализация базы данных

    # ✅ Подключаем все обработчики команд
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(check_router)
    dp.include_router(generate_router)
    dp.include_router(common_router)

    if IS_LOCAL:
        await bot.delete_webhook()  # ❗ Отключаем Webhook перед Polling
        logging.info("🛑 Webhook отключён! Бот работает через Polling.")
    else:
        try:
            await bot.delete_webhook()  # ❗ Удаляем старый Webhook перед установкой нового
            await bot.set_webhook(WEBHOOK_URL)  # 🔗 Устанавливаем Webhook
            logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
        except Exception as e:
            logging.error(f"❌ Ошибка при установке Webhook: {e}")

async def on_shutdown(_):
    """Остановка бота"""
    logging.info("🚨 Бот остановлен")

async def handle_update(request):
    """Обработчик Webhook (принимает входящие запросы от Telegram)"""
    update = await request.json()  # Получаем JSON
    await dp.feed_update(bot=bot, update=update)  # Передаём в aiogram
    return web.Response()  # Отправляем OK

async def handle_root(request):
    """Проверка работы бота (если заходишь в браузер)"""
    return web.Response(text="✅ Бот работает!", content_type="text/plain")

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
        app.router.add_get("/", handle_root)  # Обработчик для проверки работы бота
        app.router.add_post(WEBHOOK_PATH, handle_update)  # Webhook обработчик
        app.on_shutdown.append(on_shutdown)  # Добавляем обработчик остановки
        return app

# === 6️⃣ Запуск ===
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = loop.run_until_complete(main())  # Запускаем main()

    if not IS_LOCAL:
        # Только для режима Webhook (сервер)
        web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
