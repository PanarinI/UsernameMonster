from aiogram.types import BotCommand

async def set_bot_commands(bot):
    """Устанавливает команды бота (BotFather-style меню)."""
    commands = [
        BotCommand(command="/check", description="🔍 Проверить username"),
        BotCommand(command="/help", description="ℹ️ Помощь по боту")
    ]
    await bot.set_my_commands(commands)

    await bot.set_my_description(
        "🔹 Этот бот проверяет доступность username в Telegram.\n"
        "📌 Доступные команды:\n"
        "1️⃣ /check [username] - Проверить доступность username\n"
        "2️⃣ /help - Помощь по работе с ботом"
    )
