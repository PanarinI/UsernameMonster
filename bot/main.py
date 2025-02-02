import asyncio
from setup import bot, dp
from handlers.start import start_router
from handlers.generate import generate_router
from handlers.check import check_router
from handlers.common import common_router
from handlers.help import help_router


async def main():
    """Запуск бота"""
    # Регистрируем обработчики
    dp.include_router(start_router)
    dp.include_router(generate_router)
    dp.include_router(check_router)
    dp.include_router(common_router)
    dp.include_router(help_router)
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())  # Асинхронный запуск



