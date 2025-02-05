from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # Для хранения состояний
from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Создаём объект бота
bot = Bot(token=BOT_TOKEN)
if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN not found in .env file")

# Создаём объект диспетчера (обратите внимание, что без параметра bot в Dispatcher)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)  # Здесь не передаем bot как позиционный аргумент
dp.bot = bot  # Привязываем объект бота к диспетчеру вручную

