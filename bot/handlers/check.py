from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram import Bot
from aiogram.fsm.context import FSMContext
import re
from services.check import check_username_availability
from .states import CheckUsernameStates  # Импорт состояний
from keyboards.check import check_result_kb  # Импорт клавиатуры
from keyboards.main_menu import main_menu  # Импорт клавиатуры главного меню

check_router = Router()  # Создаём Router

def is_valid_username(username: str) -> bool:
    """
    Проверяет, соответствует ли username правилам Telegram.
    """
    pattern = r"^[a-zA-Z0-9_]{5,32}$"
    return bool(re.match(pattern, username))

@check_router.callback_query(F.data == "check")
async def cmd_check(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Проверить username".
    """
    await query.message.answer("Введите username для проверки (без @):")
    await state.set_state(CheckUsernameStates.waiting_for_username)
    await query.answer()

@check_router.message(CheckUsernameStates.waiting_for_username)
async def check_username(message: types.Message, bot: Bot, state: FSMContext):
    """
    Обработчик для введённого username.
    Проверяет корректность и доступность username.
    """
    username = message.text.strip()

    # Проверяем корректность username
    if not is_valid_username(username):
        await message.answer(
            "❌ Некорректный username. Убедитесь, что:\n"
            "1. Длина username от 5 до 32 символов.\n"
            "2. Используются только латинские буквы (a-z, A-Z), цифры (0-9) и нижнее подчёркивание (_).\n"
            "3. Нет пробелов, дефисов, точек или специальных символов.\n\n"
            "Попробуйте ещё раз:"
        )
        return

    # Если username корректен, проверяем его доступность
    result = await check_username_availability(bot, username)
    if result == "Свободно":
        await message.answer(
            f"✅ Имя @{username} свободно!",
            reply_markup=check_result_kb()  # Добавляем клавиатуру
        )
    elif result == "Занято":
        await message.answer(
            f"❌ Имя @{username} занято.",
            reply_markup=check_result_kb()  # Добавляем клавиатуру
        )
    else:
        await message.answer(
            f"⚠️ Не удалось определить доступность @{username}.",
            reply_markup=check_result_kb()  # Добавляем клавиатуру
        )
    await state.clear()  # Сброс состояния после завершения

@check_router.callback_query(F.data == "back_to_main")
async def back_to_main(query: types.CallbackQuery):
    """
    Обработчик для кнопки "Назад в главное меню".
    """
    await query.message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=main_menu()  # Показываем главное меню
    )
    await query.answer()