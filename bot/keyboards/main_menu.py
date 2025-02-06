from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb() -> InlineKeyboardMarkup:
    """Главное меню с тремя кнопками"""
    kb_list = [
        [InlineKeyboardButton(text="🎲 Сгенерировать username", callback_data="generate")],
        [InlineKeyboardButton(text="🔍 Проверить username", callback_data="check")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard


def back_to_main_kb() -> InlineKeyboardMarkup:
    """Клавиатура с одной кнопкой возврата в меню"""
    kb_list = [
        [InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_main")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard