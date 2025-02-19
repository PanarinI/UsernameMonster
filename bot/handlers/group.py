import logging
import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from services.generate import get_available_usernames  # Генерация никнеймов
import config

group_router = Router()

@group_router.message(Command("namehunt"))
async def send_namehunt(message: types.Message):
    """Обработчик команды /namehunt в группе"""
    logging.info(f"📩 Команда /namehunt от {message.from_user.username} в группе {message.chat.id}")

    # 📌 Извлекаем контекст (если есть)
    command_parts = message.text.split(maxsplit=1)
    context_text = command_parts[1] if len(command_parts) > 1 else "без темы"

    logging.info(f"🔍 Используем контекст: '{context_text}'")

    try:
        # 🔄 Вызываем AI для генерации никнеймов (без стиля)
        usernames = await asyncio.wait_for(
            get_available_usernames(None, context_text, None, config.AVAILABLE_USERNAME_COUNT),
            timeout=config.GEN_TIMEOUT
        )

        # Если нет результатов – сообщаем пользователю
        if not usernames:
            await message.reply("❌ Не удалось поймать имена. Попробуйте другой запрос!")
            return

        # 📩 Формируем текст с никнеймами, добавляя @ перед каждым
        usernames_text = "\n".join(f"- @{u}" for u in usernames)
        response_text = f"🎭 Вот твои уникальные имена на тему \"{context_text}\":\n{usernames_text}"

        await message.reply(response_text)

    except asyncio.TimeoutError:
        logging.error("❌ Ошибка: генерация заняла слишком много времени!")
        await message.reply("⏳ Имялов искал слишком долго. Попробуйте позже.")

    except Exception as e:
        logging.error(f"❌ Ошибка генерации: {e}")
        await message.reply("❌ Произошла ошибка при генерации имени. Попробуйте ещё раз!")
