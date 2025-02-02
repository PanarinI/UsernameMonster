from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    """Главное меню с двумя кнопками"""
    kb_list = [
        [InlineKeyboardButton(text="Сгенерировать username", callback_data="generate")],
        [InlineKeyboardButton(text="Проверить username", callback_data="check")],
        [InlineKeyboardButton(text="Помощь", callback_data="help")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def help_menu() -> InlineKeyboardMarkup:
    """Клавиатура для помощи с одной кнопкой"""
    kb_list = [
        [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard