from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

GROUP_URL = "https://t.me/bot_and_kot"  # 🔥 Замени на свою группу!

def main_menu_kb() -> InlineKeyboardMarkup:
    """Главное меню с четырьмя кнопками, включая вступление в группу"""
    kb_list = [
        [InlineKeyboardButton(text="🎲 Сгенерировать username", callback_data="generate")],
        [InlineKeyboardButton(text="🔍 Проверить username", callback_data="check")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")],
        [InlineKeyboardButton(text="🔥 Вступить в группу Bot&Kot", url=GROUP_URL)]  # ✅ Добавляем кнопку!
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