import asyncpg
import os
import logging
from dotenv import load_dotenv
import config
# Загружаем переменные окружения
load_dotenv()

DB_CONFIG = {
    "database": os.getenv("DTBS"),
    "user": os.getenv("USER"),
    "password": os.getenv("PSWRD"),
    "host": os.getenv("HOST")
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Путь к `database.py`
sql_path = os.path.join(BASE_DIR, "insert_username.sql") # выполяем SQL INSERT (добавляем username новой строкой)

with open(sql_path, "r", encoding="utf-8") as file:
    INSERT_SQL = file.read()



pool = None  # Глобальный пул соединений

async def init_db_pool():
    """Создаёт пул соединений к БД при запуске приложения."""
    global pool
    pool = await asyncpg.create_pool(**DB_CONFIG)
    logging.info("✅ Пул соединений к БД создан.")

async def close_db_pool():
    """Закрывает пул соединений при завершении работы."""
    global pool
    if pool:
        await pool.close()
        logging.info("✅ Пул соединений закрыт.")

async def get_connection():
    """Получает соединение из пула."""
    global pool
    if not pool: # Если пул не создан, создаём его
        await init_db_pool()
    return await pool.acquire() # Берём соединение из пула

async def init_db():
    """Создаёт таблицу, если её нет."""
    conn = await get_connection()
    try:
        with open("database/create_table.sql", "r", encoding="utf-8") as file:
            create_table = file.read() # Читаем SQL из файла

        await conn.execute(create_table) # Выполняем SQL в БД
        logging.info("✅ Таблица 'generated_usernames' проверена/создана.")
    except Exception as e:
        logging.error(f"❌ Ошибка при создании таблицы: {e}")
    finally:
        await pool.release(conn)  # Освобождаем соединение


async def save_username_to_db(username: str, status: str, context: str, category: str, llm: str):
    """Сохраняет username в базу данных."""
    if len(context) > config.MAX_CONTEXT_LENGTH:
        logging.warning(f"⚠️ Контекст слишком длинный ({len(context)} символов), обрезаем до {config.    MAX_CONTEXT_LENGTH}.")
        context = context[:config.MAX_CONTEXT_LENGTH]  # Обрезаем строку до нужной длины

    conn = await get_connection()
    try:
        await conn.execute(INSERT_SQL, username, status, category, context, llm)
        log_message = f"✅ Добавлен в БД: @{username} | {status} | {category} | {context} | {llm}"
        logging.info(log_message)
        print(log_message)
    except Exception as e:
        logging.error(f"❌ Ошибка при сохранении в БД: {e}")
    finally:
        await pool.release(conn)  # Освобождаем соединение

