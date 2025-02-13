CREATE TABLE IF NOT EXISTS userrrs (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- по умолчанию все таблицы создаются внутри схемы public. Это означает, что её полное имя: public.users
