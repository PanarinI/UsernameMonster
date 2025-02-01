def generate_unique_username(n: int, context: str = "") -> list:
    """
    Заглушка для генерации username.
    Пока просто возвращает список из n фиктивных имен.
    При желании можно использовать context для дальнейшей логики.
    """
    return [f"user_{i}" for i in range(1, n + 1)]
