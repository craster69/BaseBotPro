import sys
import os

# Добавляем путь к корневой директории проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(project_root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FintechBot.settings")

import django
django.setup()

from bot.routers import routers
from bot.config import bot, Config
from bot.middlewares.base_middlewares import middlewares
from bot.base_enums import RunTypeEnum, LanguageEnum
from bot.utils.base_utils import get_enums, logging_setup, logger

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Update, BotCommand

from redis.asyncio import Redis
from redis import exceptions as redis_exceptions

import asyncio

from typing import Coroutine, Dict

# from fastapi import FastAPI

# from uvicorn import Server, Config as UConfig

# from contextlib import asynccontextmanager


async def get_memory_storage() -> RedisStorage | MemoryStorage:
    """
    Взять хранилище для состояний бота
    """
    redis = Redis(
        host=Config.redis.REDIS_HOST,
        port=Config.redis.REDIS_PORT
    )
    try:
        await redis.ping()
    except redis_exceptions.ConnectionError:
        logger.warning('Failed to connect to Redis...')
        return MemoryStorage()
    else:
        logger.success('Redis is connected!')
        return RedisStorage(redis=redis)


# async def run_webhook(dp: Dispatcher, bot: Bot) -> None:
#     """
#     запуск бота через webhook
    
#     :dp - отслеживает все events, которые приходят боту
#     :bot - объект бота
#     """
#     WEBHOOK_PATH = f"/bot/{Config.tg_bot.TOKEN}"
#     WEBHOOK_URL = Config.tg_bot.WEBHOOK_URL + WEBHOOK_PATH
    
#     @asynccontextmanager
#     async def lifespan(app: FastAPI):
#         # --- STARTUP ---
#         webhook_info = await bot.get_webhook_info()
#         if webhook_info.url != WEBHOOK_URL:
#             await bot.set_webhook(url=WEBHOOK_URL)
        
#         yield  # Приложение работает

#         # --- SHUTDOWN ---
#         await bot.session.close()
#         logger.info("Остановка бота...")
    
#     app = FastAPI(lifespan=lifespan)
        
#     @app.post(WEBHOOK_PATH)
#     async def bot_webhook(update: dict):
#         """отслежка events от Telegram для бота"""
#         print(update)
#         try:
#             telegram_update = Update(**update)
#             await dp.feed_update(bot=bot, update=telegram_update)
#         except Exception as _ex:
#             logger.error(f'Ошибка: [{type(_ex).__name__}]: {_ex}')
    
#     config = UConfig(app)
#     server = Server(config)
#     await server.serve()


async def run_bot(run_type: RunTypeEnum, dp: Dispatcher, bot: Bot) -> None:
    """
    запуск бота по выбранному методу
    """
    run_dict: Dict[str, Coroutine] = {
        RunTypeEnum.POLLING.value: lambda: dp.start_polling(bot),
        # RunTypeEnum.WEBHOOK.value: lambda: run_webhook(dp, bot)
    }
    await run_dict[run_type]()


def include_middlewares(dp: Dispatcher) -> None:
    for m in middlewares:
        dp.update.middleware(m)


async def set_commands() -> None:
    commands = [
        BotCommand(command=f'/start', description='Главное меню'),
        BotCommand(command=f'/help', description='Помощь'),
        BotCommand(
            command=f'/choose_language', 
            description=f'Смена языка {" | ".join(get_enums(LanguageEnum))}'
        ),
    ]

    await bot.set_my_commands(commands)


async def main() -> None:
    """запуск проекта"""
    try:
        dp: Dispatcher = Dispatcher(storage=await get_memory_storage())
        include_middlewares(dp)
        dp.include_routers(*routers)
        
        await bot.delete_webhook(drop_pending_updates=True)
        await set_commands()
        logger.success(f'Bot "{(await bot.get_my_name()).name}" launched via method "{Config.tg_bot.RUN_TYPE.upper()}"')
        
        await run_bot(Config.tg_bot.RUN_TYPE, dp, bot)
        
    except Exception as _ex:
        logger.error(f'Error: [{type(_ex).__name__}]: {_ex}')


if __name__ == '__main__':
    try:
        logging_setup()
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopping bot...")
