import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import back_to_main_kb
from texts import get_help_text  # Импортируем текст справки


help_router = Router()  # Создаём Router


@help_router.message(Command("help"))  # ✅ Регистрируем ДО обработчиков состояний
async def cmd_help(message: types.Message, state: FSMContext):
    """Обработчик команды /help."""
    await state.clear()  # ✅ Принудительно очищаем ВСЕ состояния перед обработкой команды
    await asyncio.sleep(0.05)  # ✅ Даём FSM время сброситься

    await message.answer(
        get_help_text(),
        parse_mode="Markdown",  # ✅ Используем одинаковый Markdown
        reply_markup=back_to_main_kb(),
        disable_web_page_preview=True  # ✅ Отключаем превью ссылки
    )


@help_router.callback_query(F.data == "help")
async def handle_help(query: types.CallbackQuery, state: FSMContext):
    """Обработчик для кнопки "Помощь"."""
    await state.clear()
    await asyncio.sleep(0.05)
    await query.answer()
    await query.message.answer(
        get_help_text(),
        parse_mode="Markdown",  # ✅ Такой же режим Markdown
        reply_markup=back_to_main_kb(),
        disable_web_page_preview=True  # ✅ Отключаем превью ссылки
    )


