# Создание Inline-Клавиатуры в aiogram 3.x

В версии aiogram 3.x объект InlineKeyboardMarkup реализован на основе Pydantic, поэтому для его создания необходимо передавать обязательный параметр inline_keyboard, представляющий собой список списков объектов InlineKeyboardButton. Рекомендуемый способ создания клавиатуры – сначала сформировать список кнопок в виде списка списков, а затем создать объект разметки, передав этот список в параметр inline_keyboard.

Пример рабочего кода:


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def generate_username_kb(usernames: list) -> InlineKeyboardMarkup:
    # Формируем список строк клавиатуры. Каждая строка – список из одной или нескольких кнопок.
    kb_list = [
        [InlineKeyboardButton(text=username, callback_data=f"username:{username}")]
        for username in usernames
    ]
    # Добавляем дополнительный ряд с двумя кнопками: "Сгенерировать ещё раз" и "Назад в главное меню"
    kb_list.append([
        InlineKeyboardButton(text="Сгенерировать ещё раз", callback_data="regenerate"),
        InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_main")
    ])
    # Создаём объект клавиатуры, передавая список кнопок в параметр inline_keyboard
    return InlineKeyboardMarkup(inline_keyboard=kb_list)
Важно:

Обязательный параметр: При создании клавиатуры необходимо передавать параметр inline_keyboard – пустой список по умолчанию (например, InlineKeyboardMarkup(inline_keyboard=[])) не сработает, если затем не задать нужную структуру.
Структура: Список кнопок должен быть организован как список списков – каждая внутренняя группа кнопок формирует одну строку клавиатуры.
Совместимость: Этот способ гарантированно работает в aiogram 3.x и соответствует требованиям Pydantic для валидации моделей.
Этот метод был проверен и гарантированно работает в проекте. Обязательно используйте именно такой подход для формирования инлайн-клавиатуры, чтобы избежать ошибок валидации и обеспечить корректное отображение кнопок.


















Правильное создание InlineKeyboardButton:Важно помнить, что при создании InlineKeyboardButton нужно использовать именованные параметры. То есть вместо:

InlineKeyboardButton("Сгенерировать username", callback_data="generate")
Нужно писать:

InlineKeyboardButton(text="Сгенерировать username", callback_data="generate")
Параметры должны передаваться как ключевые слова (text= и callback_data=).
Форматирование списка кнопок:Кнопки должны быть организованы в двумерный список, где каждый элемент представляет собой строку кнопок. Например:

kb_list = [
    [InlineKeyboardButton(text="Кнопка 1", callback_data="action_1")],
    [InlineKeyboardButton(text="Кнопка 2", callback_data="action_2")]
]
Это позволяет создавать кнопки, расположенные друг под другом.
Передача списка кнопок в InlineKeyboardMarkup:Список кнопок передается в конструктор InlineKeyboardMarkup через именованный параметр inline_keyboard:

keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
Эти три ключевых момента помогут вам избегать подобных ошибок в будущем.