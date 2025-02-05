# Changelog

## [Released]
Все заметные изменения проекта фиксируются в этом файле.

## [Unreleased]
- Тут фиксируются изменения, которые ещё не вошли в релиз.


## [0.1.1] - 2025-02-04
### Added
- составлен TECH_FLOW +mmd diagram (3 версии)
- в config вынесены константы GENERATED_USERNAME_COUNT (сколько выводится на экран) и AVAILABLE_USERNAME_COUNT (сколько генерируется за 1 раз)
- прокомментированы service.generate, service.check, handlers.generate
- составлен README
- добавлены новые задачи
- 
## [0.1.0] - 2025-02-03  <-- Первая версия MVP
### Added
- Первая рабочая версия бота.
- Проверка доступности Telegram-юзернеймов.
- Генерация уникальных username.
- Добавлено логирование DEBUG (в фокусе - service.generate)  в bot.log
- Определена структура документации - README, ARCHITECTURE, TECH_FLOW (+mmd diagram), USER_FLOW (+mmd diagram), SETUP, FUTURE_PLANS, CHANGELOG
- Конфиденциальные данные перенесены в .env (python-dotenv)
- 

## [0.0.2] - 2025-01-30
### Added
- Прописана логика функции генерации username
- Базовая концепция UI

## [0.0.1] - 2025-1-27
### Added
- Первый набросок проекта.
- Первый рабочий код - функция проверки досступности username
