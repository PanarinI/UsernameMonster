INSERT INTO generated_usernames (username, status, category, context, llm, style)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (username) DO NOTHING;
