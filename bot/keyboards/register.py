from aiogram.filters import Command  # ✅ Правильно для aiogram 3.x

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def register_keyboard(username):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    keyboard.add(InlineKeyboardButton("✅ Да", callback_data=f"register_{username}"))
    keyboard.add(InlineKeyboardButton("❌ Нет", callback_data="menu"))
    return keyboard




keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да", f"register_{username}")],
    [InlineKeyboardButton(text="❌ Нет", callback_data="menu")],
])
