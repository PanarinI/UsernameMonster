import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import StateFilter
from config import BOT_TOKEN
from handlers.username_check import handle_check_command, handle_username_input
from utils.bot_setup import set_bot_commands

# Создаём экземпляры бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем обработчики
dp.message.register(handle_check_command, F.text == "/check")  # Обработчик команды /check
dp.message.register(handle_username_input, StateFilter("UsernameCheck:waiting_for_username"))  # FSM фильтр

async def main():
    """Запуск бота"""
    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(bot)  # Устанавливаем команды бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
