from aiogram import BaseMiddleware
from aiogram.types import Message
import logging

class CleanupMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.last_bot_messages = {}

    async def __call__(self, handler, event: Message, data: dict):
        chat_id = event.chat.id
        if chat_id in self.last_bot_messages:
            try:
                logging.info(f"Удаляю сообщение: {self.last_bot_messages[chat_id]}")
                await event.bot.delete_message(chat_id, self.last_bot_messages[chat_id])
            except Exception as e:
                logging.error(f"Ошибка при удалении сообщения: {e}")

        result = await handler(event, data)

        if isinstance(result, Message):
            self.last_bot_messages[chat_id] = result.message_id
            logging.info(f"Сохраняю новое сообщение: {result.message_id}")

        return result
