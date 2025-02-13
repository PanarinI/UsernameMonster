import asyncpg
import asyncio
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

DTBS = os.getenv("DTBS")
USER = os.getenv("USER")
PSWRD = os.getenv("PSWRD")
HOST = os.getenv("HOST")

async def test_connection():
    try:
        conn = await asyncpg.connect(
            database=DTBS,
            user=USER,
            password=PSWRD,
            host=HOST
        )
        print("✅ Подключение к базе данных прошло успешно!")
        await conn.close()
    except Exception as e:
        print("❌ Ошибка подключения к базе:", e)

async def run_sql_file(filename):
    try:
        conn = await asyncpg.connect(
            database=DTBS,
            user=USER,
            password=PSWRD,
            host=HOST
        )
        with open(filename, 'r', encoding='utf-8') as file:
            sql_code = file.read()

        print("📄 SQL-код для выполнения:\n", sql_code)

        # Пробуем выполнить SQL-код
        await conn.execute(sql_code)
        print("✅ SQL-код выполнен успешно!")

        await conn.close()
    except Exception as e:
        print("❌ Ошибка при выполнении SQL:", e)

async def check_tables():
    try:
        conn = await asyncpg.connect(
            database=DTBS,
            user=USER,
            password=PSWRD,
            host=HOST
        )

        result = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        print("📋 Список таблиц в базе:")
        for row in result:
            print("-", row['tablename'])

        await conn.close()
    except Exception as e:
        print("❌ Ошибка при проверке таблиц:", e)

async def main():
    await test_connection()  # Проверка подключения
    await run_sql_file("/bot/database/schema.sql")  # Запуск SQL-кода
    await check_tables()  # Проверка списка таблиц

asyncio.run(main())
