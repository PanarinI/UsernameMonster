from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def check_result_kb() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с кнопками "Проверить другое имя" и "Назад в главное меню".
    """
    keyboard = [
        [
            InlineKeyboardButton(text="Проверить другое имя", callback_data="check"),
            InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)