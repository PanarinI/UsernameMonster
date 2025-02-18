-- Добавляем новый столбец `style`, значение по умолчанию NULL (можно заменить на 'None')
ALTER TABLE generated_usernames ADD COLUMN style TEXT;

-- Обновляем старые записи, чтобы в новом столбце style не было NULL, а был 'None'
UPDATE generated_usernames SET style = 'None' WHERE style IS NULL;

