CREATE TEMP TABLE temp_usernames (username VARCHAR(32));

COPY public.temp_usernames (username) FROM 'F:\\PythonProject\\UsernameBot\\db\\DA\\usernames.csv' WITH (FORMAT csv, HEADER true);

INSERT INTO public.generated_usernames (username, status, category, context, style, llm, created_at)
SELECT
    username,
    'продано' AS status,
    '!frgm_autofill' AS category,
    '!frgm_autofill' AS context,
    '!frgm_autofill' AS style,
    '!frgm_autofill' AS llm,
    '2025-02-03 12:00:00'::timestamp AS created_at
FROM public.temp_usernames
ON CONFLICT (username) DO NOTHING;
