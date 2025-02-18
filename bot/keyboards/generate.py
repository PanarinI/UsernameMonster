from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_username_kb(usernames: list) -> InlineKeyboardMarkup:
    kb_list = [
        [InlineKeyboardButton(text=username, callback_data=f"username:{username}")]
        for username in usernames # для каждого username в списке usernames -- список создается в process_context_input (handlers.generate)
    ]
    kb_list.append([
        InlineKeyboardButton(text=" Попробовать снова", callback_data="generate"),
        InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=kb_list)

def error_retry_kb() -> InlineKeyboardMarkup:
    """Клавиатура для ошибки: повторить генерацию или вернуться в главное меню."""
    kb_list = [
        [InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="generate")],
        [InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb_list)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def styles_kb():
    """Генерирует клавиатуру с вариантами стилей username."""
    buttons = [
        [InlineKeyboardButton(text="⚡ Эпичный", callback_data="epic")],
        [InlineKeyboardButton(text="🎩 Строгий", callback_data="strict")],
        [InlineKeyboardButton(text="🎭 Фанковый", callback_data="funky")],
        [InlineKeyboardButton(text="🖤 Минималистичный", callback_data="minimal")],
        [InlineKeyboardButton(text="🤡 Кринжовый", callback_data="cringe")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

