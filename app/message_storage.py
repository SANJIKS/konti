from collections import defaultdict
from aiogram import types

user_message_ids = defaultdict(list)

async def add_messages(user_id, message_ids):
    if isinstance(message_ids, list):
        user_message_ids[user_id].extend(message_ids)
    else:
        user_message_ids[user_id].append(message_ids)

async def remove_specific_message(user_id, message_id, bot):
    if user_id in user_message_ids and message_id in user_message_ids[user_id]:
        try:
            await bot.delete_message(chat_id=user_id, message_id=message_id)
            user_message_ids[user_id].remove(message_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

async def remove_all_messages(user_id, bot):
    if user_id in user_message_ids:
        for message_id in user_message_ids[user_id]:
            try:
                await bot.delete_message(chat_id=user_id, message_id=message_id)
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")
        user_message_ids[user_id].clear()

async def get_last_messages(user_id):
    return user_message_ids.get(user_id, [])
