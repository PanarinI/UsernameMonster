F:\PostgreSQL\bin\psql.exe -U postgres #войти в БД
pass - Pdjyjr2&
#если ошибка:  "more" не является внутренней или внешней командой"
\pset pager off # если ошибка, если psql уже открыт
F:\PostgreSQL\bin\psql.exe -U postgres -d NameHunt ## через username postgres




Команды:
\l - список всех БД на сервере
\c NameHunt - работа внутри конкретной БД ### Вы подключены к базе данных "NameHunt" как пользователь "postgres".
\dt - проверить список таблиц

\d users - структура таблицы users





SELECT tablename FROM pg_tables WHERE schemaname = 'public';  -- проверить, какие таблицы есть в базе



SELECT current_database()

INSERT INTO bot_responses (user_id, message, bot_reply)
VALUES (12345, 'Привет, бот!', 'Привет! Как я могу помочь?');

CREATE TABLE bot_responses (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    bot_reply TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



SELECT schema_name FROM information_schema.schemata; -- список схем в базе

