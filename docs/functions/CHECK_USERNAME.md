**Общая последовательность**
## Первичная проверка через Telegram API

#### Метод: bot.get_chat(f"@{username}")
#### Если успешно найден, username занят.
#### Если ошибка chat not found, переходим к Fragment.

## Запрос к Fragment

#### URL https://fragment.com/username/{username} проверяет существование username.
#### Если произошел редирект на https://fragment.com/?query={username}, имя свободно.
#### Если редиректа нет, парсим страницу.

## Анализ страницы /username/{username}

### Ищем элемент tm-section-header-status, содержащий один из статусов:
#### Available → Доступно для покупки.
#### Sold → Продано.
#### Taken → Занято.

## Обработка ошибок

Если Telegram API возвращает TelegramForbiddenError, username занят.
Если Fragment недоступен, результат Невозможно определить.
