import os

from typing import Type

from dotenv import load_dotenv

from bot.type_defs.base_types import (
    ConfigType,
    DatabaseType,
    TgBotType,
    RedisType,
    ChatsType
)
from bot.base_enums import (
    EnvEnum,
    RunTypeEnum,
    ParseModeEnum
)

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


load_dotenv()


def get_env(env_str: EnvEnum, return_type: Type[int] | Type[str] = str) -> int | str:
    """получение данных из .env"""
    return return_type(os.getenv(env_str.value))


Config: ConfigType = ConfigType(
    tg_bot=TgBotType(
        TOKEN=get_env(EnvEnum.TOKEN_TG_BOT),
        PARSE_MODE=ParseModeEnum.HTML.value,
        RUN_TYPE=RunTypeEnum.POLLING.value,
        WEBHOOK_URL=get_env(EnvEnum.WEBHOOK_URL),
        PAGE_SIZE=6
    ),
    database=DatabaseType(
        DB_HOST=get_env(EnvEnum.DB_HOST),
        DB_NAME=get_env(EnvEnum.DB_NAME),
        DB_PASSWORD=get_env(EnvEnum.DB_PASSWORD),
        DB_PORT=get_env(EnvEnum.DB_PORT, int),
        DB_USER=get_env(EnvEnum.DB_USER)
    ),
    redis=RedisType(
        REDIS_HOST=get_env(EnvEnum.REDIS_HOST),
        REDIS_PORT=get_env(EnvEnum.REDIS_PORT, int)
    ),
    chats=ChatsType(
        MODERATOR=get_env(EnvEnum.MODERATOR_CHAT_ID, int)
    ),
)

bot: Bot = Bot(
    token=Config.tg_bot.TOKEN,
    default=DefaultBotProperties(
        parse_mode=Config.tg_bot.PARSE_MODE,
        link_preview_is_disabled=True
    )
)
