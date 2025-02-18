# states.py
from aiogram.fsm.state import StatesGroup, State

class GenerateUsernameStates(StatesGroup):
    waiting_for_context = State()  # Ожидание ввода контекста
    waiting_for_style = State()  # Ожидание выбора стиля

class CheckUsernameStates(StatesGroup):
    waiting_for_username = State()  # Ожидание ввода username