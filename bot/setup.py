from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # Для хранения состояний
from config import BOT_TOKEN  # Импортируем токен из конфигурации

# Создаём объект бота
bot = Bot(token=BOT_TOKEN)

# Создаём объект диспетчера (обратите внимание, что без параметра bot в Dispatcher)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)  # Здесь не передаем bot как позиционный аргумент
dp.bot = bot  # Привязываем объект бота к диспетчеру вручную
