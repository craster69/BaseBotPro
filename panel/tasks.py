import asyncio

from celery import shared_task

from bot.config import bot

@shared_task
def broadcast_message(user_ids, message_text):

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_broadcast(user_ids, message_text))
    finally:
        # Не закрываем loop — Celery может переиспользовать поток
        pass


async def _broadcast(user_ids, message_text):
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=message_text)
            print(f"✅ Отправлено {user_id}")
        except Exception as e:
            print(f"❌ Ошибка {user_id}: {e}")