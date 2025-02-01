from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    """Главное меню с двумя кнопками"""
    kb_list = [
        [InlineKeyboardButton(text="Сгенерировать username", callback_data="generate")],
        [InlineKeyboardButton(text="Проверить username", callback_data="check")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard