INSERT INTO generated_usernames (username, status, category, context, llm)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (username) DO NOTHING;
