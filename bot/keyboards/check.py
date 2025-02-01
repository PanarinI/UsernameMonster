from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def after_check_keyboard():
    """Кнопки после проверки username"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Проверить другой", callback_data="check")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")]
    ])
    return keyboard

