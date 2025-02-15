import asyncio
import logging
import re
import time
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from .states import CheckUsernameStates
from keyboards.check import check_result_kb
from keyboards.main_menu import main_menu_kb, back_to_main_kb
from services.check import check_username_availability


check_router = Router()  # Создаём Router


### ✅ 1. ОБРАБОТЧИК КОМАНДЫ /check
@check_router.message(Command("check"))
async def cmd_check_slash(message: types.Message, state: FSMContext):
    """
    Обработчик для команды /check.
    """
    logging.info(f"📩 Команда /check от {message.from_user.username} (id={message.from_user.id})")

    await state.clear()  # ⛔ Принудительно очищаем ВСЕ состояния
    await asyncio.sleep(0.05)  # 🔄 Даем FSM время сброситься

    await message.answer("Введите username для проверки (без @):",
                         reply_markup=back_to_main_kb() # Добавляем кнопку "🔙 В меню"
    )
    await state.set_state(CheckUsernameStates.waiting_for_username)

### ✅ 2. ОБРАБОТЧИК INLINE-КНОПКИ "Проверить username"
@check_router.callback_query(F.data == "check")
async def cmd_check(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Проверить username".
    """
    logging.info(f"📩 Нажата кнопка 'Проверить username' от {query.from_user.username} (id={query.from_user.id})")

    await state.clear()  # ⛔ Очищаем состояние перед новой командой
    await asyncio.sleep(0.05)  # 🔄 Даем FSM время очиститься

    await query.message.answer("Введите username для проверки (без @):",
                               reply_markup=back_to_main_kb()
    )
    await state.set_state(CheckUsernameStates.waiting_for_username)
    await query.answer()

### ✅ 3. ПРОВЕРКА КОРРЕКТНОСТИ ВВЕДЕННОГО USERNAME
def is_valid_username(username: str) -> bool:
    """
    Проверяет, соответствует ли username правилам Telegram, в т.ч. не начинается и не заканчивается на нижнее подчеркивание.
    """
    # Регулярное выражение
    pattern = r"^(?!_)[a-zA-Z0-9_]{5,32}(?<!_)$"
    return bool(re.match(pattern, username))


### ✅ 4. ОБРАБОТЧИК ВВОДА USERNAME
@check_router.message(CheckUsernameStates.waiting_for_username)
async def check_username(message: types.Message, bot: Bot, state: FSMContext):
    """
    Обработчик для введённого username.
    Проверяет корректность и доступность username.
    """

    username = message.text.strip()
    check_start = time.time()  # ✅ Фиксируем время начала проверки

    logging.info(f"🔍 Начало проверки username: @{username} (от {message.from_user.username}, id={message.from_user.id})")

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


    # Если username корректен, проверяем username
    logging.info(f"🔄 Проверяем @{username} через Telegram API и Fragment...") # Логируем процесс проверки
    waiting_message = await message.answer("⌛ Проверяю..")     # ⏳ Отправляем сообщение о начале генерации
    result = await check_username_availability(username, save_to_db=True)
    logging.info(f"✅ Проверка завершена за {time.time() - check_start:.2f} сек. Результат: {result}")

    # ✅ Защита от None
    if result is None:
        logging.error(f"⚠️ Ошибка: Не удалось проверить username @{username}.")
        await message.answer("⚠️ Ошибка: не удалось проверить username. Попробуйте позже.")
        return

    # 🛑 Если Telegram API заблокировал запросы
    if result.startswith("FLOOD_CONTROL"):
        retry_seconds = int(result.split(":")[1])
        hours = retry_seconds // 3600
        minutes = (retry_seconds % 3600) // 60

        logging.warning(f"🚫 Telegram API заблокировал бота на {hours}ч {minutes}м")

        await message.answer(
            f"🚫 Бот временно заблокирован в Telegram API из-за слишком частых проверок.\n"
            f"Попробуйте снова через {hours} ч {minutes} мин.",
            reply_markup=main_menu_kb()  # Главное меню
        )

        await state.clear()  # Очистка состояния
        return

    # 🟢 Логика ответов
    logging.info(f"✅ Результат проверки @{username}: {result}")

    if result == "Свободно":
        await message.answer(f"✅ Имя @{username} свободно!", reply_markup=check_result_kb())
    elif result == "Занято":
        await message.answer(f"❌ Имя @{username} занято.", reply_markup=check_result_kb())
    elif result == "Продано":
        await message.answer(f"💰 Имя @{username} уже продано и больше недоступно.", reply_markup=check_result_kb())
    elif result == "Доступно для покупки":
        fragment_url = f"https://fragment.com/username/{username}"
        await message.answer(
            f"Имя @{username} занято, но доступно для покупки [на Fragment]({fragment_url}).",
            reply_markup=check_result_kb(),
            parse_mode="Markdown"  # Используем HTML для ссылки
        )
    elif result == "Свободно, но не на продаже":
        await message.answer(f"✅ Имя @{username} свободно!", reply_markup=check_result_kb())
    elif result == "Недоступно":
        await message.answer(f"⚠️ Имя @{username} занято, но не продаётся (Not for sale).", reply_markup=check_result_kb())
    else:
        await message.answer(f"⚠️ Не удалось определить доступность @{username}.", reply_markup=check_result_kb())

    await state.clear()  # ⛔️ Очищаем состояние после проверки


### ✅ 5. ВОЗВРАТ В ГЛАВНОЕ МЕНЮ
@check_router.callback_query(F.data == "back_to_main")
async def back_to_main(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для кнопки "Назад в меню".
    """
    logging.info(f"🔙 {query.from_user.username} вернулся в главное меню.")

    await state.clear()  # ⛔ Очистка состояния перед выходом
    await asyncio.sleep(0.05)

    await query.message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=main_menu_kb()  # Показываем главное меню
    )
    await query.answer()
