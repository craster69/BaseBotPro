import asyncio

from aiogram.types import FSInputFile, InlineKeyboardButton as IB
from aiogram.utils.keyboard import InlineKeyboardBuilder as BD

from celery import shared_task

from bot.config import bot
from bot.utils.base_utils import logger

import os

@shared_task
def broadcast_message(user_ids: list[int], message_text: str, photo_path: str = None, buttons: list[dict[str, str]] = None):

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_broadcast(user_ids, message_text, photo_path, buttons))
    finally:
        # Не закрываем loop — Celery может переиспользовать поток
        pass


async def _broadcast(user_ids: list[int], message_text: str, photo_path: str = None, buttons: list[dict[str, str]] = None):
    kb = None
    
    if buttons:
        kb = BD()
        for btn in buttons:
            print(btn.keys())
            if 'text' in btn.keys() and 'url' in btn.keys():
                kb.row(IB(text=btn['text'], url=btn['url']))
        kb = kb.as_markup()
    
    for user_id in user_ids:
        try:
            if photo_path and os.path.exists(photo_path):
                photo = FSInputFile(photo_path)
                await bot.send_photo(chat_id=user_id, photo=photo, caption=message_text or None, reply_markup=kb)
                logger.info(f"✅ Фото отправлено {user_id}")
            elif message_text:
                await bot.send_message(chat_id=user_id, text=message_text, reply_markup=kb)
                logger.info(f"✅ Сообщение отправлено {user_id}")
            else:
                logger.warning(f"⚠️ Нечего отправлять {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка {user_id}: {e}")
            
    if photo_path and os.path.exists(photo_path):
        os.remove(photo_path)
        logger.info(f"🗑️ Временный файл удалён: {photo_path}")