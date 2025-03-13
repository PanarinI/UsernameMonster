INSERT INTO generated_usernames_monster (username, status, category, context, style, llm)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (username) DO NOTHING;
