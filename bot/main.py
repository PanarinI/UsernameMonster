import time
import asyncio
import sys
import os
import logging
import config
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

            retries = 5
            for attempt in range(retries):
                try:
                    await bot.set_webhook(WEBHOOK_URL)
                    logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
                    break  # Выход из цикла, если установка прошла успешно
                except Exception as e:
                    logging.error(f"❌ Ошибка при установке Webhook на попытке #{attempt + 1}: {e}")
                    if attempt < retries - 1:  # Если не последняя попытка
                        wait_time = 2 ** attempt  # Экспоненциальная задержка
                        logging.info(f"⏳ Повторная попытка через {wait_time} секунд...")
                        await asyncio.sleep(wait_time)
                    else:
                        logging.error("❌ Превышено количество попыток установки Webhook. Бот не может продолжить.")
                        sys.exit(1)  # Прерываем запуск после максимального числа попыток
        except Exception as e:
            logging.error(f"❌ Ошибка при установке Webhook: {e}")
            sys.exit(1)  # Прерываем запуск


async def on_shutdown(_):
    """Закрытие сессии перед остановкой"""
    logging.info("🚨 Бот остановлен! Закрываю сессию...")
    try:
        await bot.session.close()
    except Exception as e:
        logging.error(f"❌ Ошибка при закрытии сессии: {e}")
    logging.info("✅ Сессия закрыта.")


import json

async def handle_update(request):
    """Обработчик Webhook (принимает входящие запросы от Telegram)"""
    time_start = time.time()
    raw_text = await request.text()

    try:
        update_data = json.loads(raw_text)  # ✅ Разбираем JSON
        update_id = update_data.get("update_id", "неизвестно")
        current_time = int(time.time())

        # Проверяем, нет ли устаревших событий
        if "message" in update_data:
            message_time = update_data["message"]["date"]
            if current_time - message_time > 15:  # Больше 15 секунд? Игнорируем!
                logging.warning(f"⚠️ Старая команда ({message_time}), игнорируем.")
                return web.Response(status=200)

        if "callback_query" in update_data:
            callback = update_data["callback_query"]
            callback_time = callback.get("date", current_time)

            if current_time - callback_time > 15:
                logging.warning(f"⚠️ Старая callback-команда ({callback_time}), игнорируем.")
                return web.Response(status=200)

            # ✅ Фикс: теперь `user` определён всегда
            user = callback.get("from", {})
            message = callback.get("message", {})
            button_data = callback.get("data", "Нет данных")

            log_text = (
                f"📩 Update ID: {update_id}\n"
                f"👤 Пользователь: {user.get('first_name', 'Неизвестный')} (@{user.get('username', 'Нет юзернейма')})\n"
                f"💬 Сообщение от бота: {message.get('text', 'Без текста')}\n"
                f"🔘 Нажата кнопка: {button_data}"
            )
            logging.info(log_text)

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
        sys.exit(0)  # <-- Прерываем выполнение, чтобы Webhook НЕ запускался!

    # 🌐 Если режим Webhook
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
