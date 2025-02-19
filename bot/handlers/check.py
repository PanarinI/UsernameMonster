import asyncio
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from .states import CheckUsernameStates
from keyboards.check import check_result_kb
from keyboards.main_menu import main_menu_kb, back_to_main_kb
from services.check import check_multiple_usernames  # Исправленный импорт
import re
import logging

check_router = Router()  # Создаём Router


### ✅ 1. ОБРАБОТЧИК КОМАНДЫ /check
@check_router.message(Command("check"))
async def cmd_check_slash(message: types.Message, state: FSMContext):
    await state.clear()
    await asyncio.sleep(0.05)

    await message.answer("Введите username для проверки (без @):",
                         reply_markup=back_to_main_kb()
    )
    await state.set_state(CheckUsernameStates.waiting_for_username)


### ✅ 2. ОБРАБОТЧИК INLINE-КНОПКИ "Проверить username"
@check_router.callback_query(F.data == "check")
async def cmd_check(query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await asyncio.sleep(0.05)

    await query.message.answer("Введите username для проверки (без @):",
                               reply_markup=back_to_main_kb()
    )
    await state.set_state(CheckUsernameStates.waiting_for_username)
    await query.answer()


### ✅ 3. ПРОВЕРКА КОРРЕКТНОСТИ ВВЕДЕННОГО USERNAME
def is_valid_username(username: str) -> bool:
    pattern = r"^(?!.*__)[a-zA-Z0-9](?:[a-zA-Z0-9_]{3,30})[a-zA-Z0-9]$"
    return bool(re.match(pattern, username))


### ✅ 4. ОБРАБОТЧИК ВВОДА USERNAME + ЗАЩИТА ОТ КОМАНД
@check_router.message(CheckUsernameStates.waiting_for_username)
async def check_username(message: types.Message, bot: Bot, state: FSMContext):
    username = message.text.strip()
    logging.info(f"🔍 Проверка username: @{username}")

    if username.startswith("/"):
        await state.clear()
        await message.answer("⚠️ Вы ввели команду вместо username. Введите команду заново.")
        return

    if not is_valid_username(username):
        await message.answer(
            "❌ Некорректный username. Убедитесь, что:\n"
            "1. Длина от 5 до 32 символов.\n"
            "2. Только латинские буквы, цифры и нижнее подчёркивание (но не в начале, не в конце и не больше 1 подряд).\n"
            "3. Нет пробелов, дефисов, точек или специальных символов.\n\n"
            "Попробуйте ещё раз:"
        )
        return

    # ✅ Правильный вызов проверки одного username через check_multiple_usernames
    results = await check_multiple_usernames([username], save_to_db=True)
    result = results.get(username, "Невозможно определить")

    if result == "Свободно":
        await message.answer(f"✅ Имя @{username} свободно!", reply_markup=check_result_kb())
    elif result == "Занято":
        await message.answer(f"❌ Имя @{username} занято.", reply_markup=check_result_kb())
    elif result == "Продано":
        await message.answer(f"💰 Имя @{username} уже продано.", reply_markup=check_result_kb())
    elif result == "Доступно для покупки":
        fragment_url = f"https://fragment.com/username/{username}"
        await message.answer(
            f"Имя @{username} занято, но доступно для покупки [на Fragment]({fragment_url}).",
            reply_markup=check_result_kb(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(f"⚠️ Не удалось определить доступность @{username}.", reply_markup=check_result_kb())

    await state.clear()


### ✅ 5. ВОЗВРАТ В ГЛАВНОЕ МЕНЮ
@check_router.callback_query(F.data == "back_to_main")
async def back_to_main(query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await asyncio.sleep(0.05)

    await query.message.answer(
        "Ты снова на главной тропе.",
        reply_markup=main_menu_kb()
    )
    await query.answer()
