import asyncio

from celery import shared_task

from bot.config import bot

@shared_task
def broadcast_message(user_ids, message_text):
    clean_ids = []
    for uid in user_ids:
        try:
            clean_ids.append(int(uid))
        except:
            pass
    asyncio.run(_broadcast(clean_ids, message_text))


async def _broadcast(user_ids, message_text):
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=message_text)
            print(f"✅ Отправлено {user_id}")
        except Exception as e:
            print(f"❌ Ошибка {user_id}: {e}")