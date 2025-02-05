from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_username_kb(usernames: list) -> InlineKeyboardMarkup:
    kb_list = [
        [InlineKeyboardButton(text=username, callback_data=f"username:{username}")]
        for username in usernames # для каждого username в списке usernames -- список создается в process_context_input (handlers.generate)
    ]
    kb_list.append([
        InlineKeyboardButton(text="Сгенерировать ещё раз", callback_data="generate"),
        InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=kb_list)
