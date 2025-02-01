from aiogram import Dispatcher
from aiogram.types import CallbackQuery

async def check_username(call: CallbackQuery) -> None:
    """Обработчик кнопки 'Проверить username'"""
    await call.message.answer("Заглушка: проверка username...")
    await call.answer()  # Ответ на callback, чтобы убрать "зависший" статус

def register_handlers_check(dp: Dispatcher) -> None:
    """Регистрируем обработчик кнопки 'Проверить'"""
    dp.callback_query.register(check_username, text="check")
