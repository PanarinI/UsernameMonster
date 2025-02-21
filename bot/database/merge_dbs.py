import psycopg2
## Сливаем локальную базу в облачную. Должно срабатывать в любой момент без потери данных. Но возможно лучше их просто будет добавлять отдельно без ID. Как новые.
# Подключаемся к локальной базе данных
local_conn = psycopg2.connect(
    dbname="NameHunt",
    user="postgres",
    password="Pdjyjr2",
    host="localhost",  # Или IP-адрес локального хоста
    port=5432
)
print("Подключение к локальной базе данных успешно!")
# Подключаемся к облачной базе данных на Amvera
cloud_conn = psycopg2.connect(
    dbname="namehunt_db",
    user="PanarinI",
    password="Pdjyjr22&",
    host="namehuntdb-panarini.db-msk0.amvera.tech",  # Хост базы на Amvera
    port=5432
)

print("Подключение к облачной базе данных успешно!")

# Создаём курсоры для выполнения запросов
local_cursor = local_conn.cursor()
cloud_cursor = cloud_conn.cursor()

try:
    # Начинаем транзакцию
    cloud_conn.autocommit = False  # Отключаем автокоммит, чтобы использовать транзакции

    # Получаем максимальный id из локальной базы
    local_cursor.execute("SELECT MAX(id) FROM public.generated_usernames")
    max_id_local = local_cursor.fetchone()[0] or 0
    print(f"Максимальный ID в локальной базе: {max_id_local}")

    # Получаем текущий id в облачной базе
    cloud_cursor.execute("SELECT MAX(id) FROM public.generated_usernames")
    max_id_cloud = cloud_cursor.fetchone()[0] or 0
    print(f"Максимальный ID в облачной базе: {max_id_cloud}")

    # Устанавливаем значение следующего id для облачной базы
    new_start_id = max(max_id_local + 1, max_id_cloud + 1)
    print(f"Следующий ID для облачной базы: {new_start_id}")

    cloud_cursor.execute(f"SELECT setval('generated_usernames_new_id_seq', {new_start_id}, false)")

    # Переносим данные из локальной базы в облачную
    local_cursor.execute("SELECT username, status, category, context, style, llm FROM public.generated_usernames")
    data_to_insert = local_cursor.fetchall()

    for row in data_to_insert:
        # Если llm пустое, заменяем на "gemini-flash-1.5"
        if row[5] is None:
            row = row[:5] + ("gemini-flash-1.5",)

        # Проверяем наличие username в облачной базе
        cloud_cursor.execute("SELECT 1 FROM public.generated_usernames WHERE username = %s", (row[0],))
        if cloud_cursor.fetchone():
            print(f"Пропускаем запись с username={row[0]}, так как она уже существует в облачной базе.")
            continue  # Пропускаем эту запись

        # Вставляем запись без id, чтобы база сама создала уникальный id
        cloud_cursor.execute(
            "INSERT INTO public.generated_usernames (username, status, category, context, style, llm) VALUES (%s, %s, %s, %s, %s, %s)",
            row
        )

    # Фиксируем изменения в облачной базе
    cloud_conn.commit()
    print("Все данные успешно перенесены без дубликатов по username!")


except Exception as e:
    # В случае ошибки откатываем изменения
    cloud_conn.rollback()
    print(f"Ошибка: {e}. Все изменения были отменены.")

finally:
    # Закрываем соединения
    local_conn.close()
    cloud_conn.close()
