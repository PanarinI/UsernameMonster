import asyncio
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from .states import CheckUsernameStates
from keyboards.check import check_result_kb
from keyboards.main_menu import main_menu
from services.check import check_username_availability
import re

check_router = Router()  # Создаём Router




### ✅ 1. ОБРАБОТЧИК КОМАНДЫ /check
@check_router.message(Command("check"))
async def cmd_check_slash(message: types.Message, state: FSMContext):
    """
    Обработчик для команды /check.
    """
    await state.clear()  # ⛔ Принудительно очищаем ВСЕ состояния
    await asyncio.sleep(0.05)  # 🔄 Даем FSM время сброситься

    await message.answer("Введите username для проверки (без @):")
    await state.set_state(CheckUsernameStates.waiting_for_username)

### ✅ 2. ОБРАБОТЧИК INLINE-КНОПКИ "Проверить username"
@check_router.callback_query(F.data == "check")
async def cmd_check(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Проверить username".
    """
    await state.clear()  # ⛔ Очищаем состояние перед новой командой
    await asyncio.sleep(0.05)  # 🔄 Даем FSM время очиститься

    await query.message.answer("Введите username для проверки (без @):")
    await state.set_state(CheckUsernameStates.waiting_for_username)
    await query.answer()


### ✅ 3. ПРОВЕРКА КОРРЕКТНОСТИ ВВЕДЕННОГО USERNAME
def is_valid_username(username: str) -> bool:
    """
    Проверяет, соответствует ли username правилам Telegram.
    """
    pattern = r"^[a-zA-Z0-9_]{5,32}$"
    return bool(re.match(pattern, username))


### ✅ 4. ОБРАБОТЧИК ВВОДА USERNAME + ЗАЩИТА ОТ КОМАНД
@check_router.message(CheckUsernameStates.waiting_for_username)
async def check_username(message: types.Message, bot: Bot, state: FSMContext):
    """
    Обработчик для введённого username.
    Проверяет корректность и доступность username.
    """

    username = message.text.strip()

    # ❗️ Если пользователь вводит КОМАНДУ в этом состоянии – сбрасываем FSM и игнорируем ввод
    if username.startswith("/"):
        await state.clear()
        await message.answer("⚠️ Вы ввели команду вместо username. Введите команду заново.")
        return

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

    await state.clear()  # ⛔️ Фикс: Принудительно очищаем состояние после проверки


### ✅ 5. ВОЗВРАТ В ГЛАВНОЕ МЕНЮ
@check_router.callback_query(F.data == "back_to_main")
async def back_to_main(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Назад в главное меню".
    """
    await state.clear()  # ⛔ Очистка состояния перед выходом
    await asyncio.sleep(0.05)

    await query.message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=main_menu()  # Показываем главное меню
    )
    await query.answer()
