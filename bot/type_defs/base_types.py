from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup as IKM

from aiogram.types import InlineKeyboardButton as IB


@dataclass(frozen=True, slots=True)
class TgBotType:
    TOKEN: str
    PARSE_MODE: str
    RUN_TYPE: str
    WEBHOOK_URL: str
    PAGE_SIZE: int


@dataclass(frozen=True, slots=True)
class DatabaseType:
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str


@dataclass(frozen=True, slots=True)
class RedisType:
    REDIS_HOST: str
    REDIS_PORT: int
    
    
@dataclass(frozen=True, slots=True)
class ChatsType:
    MODERATOR: int


@dataclass(frozen=True, slots=True)
class ConfigType:
    tg_bot: TgBotType
    database: DatabaseType
    redis: RedisType
    chats: ChatsType


@dataclass(frozen=True)
class MediaContentForMsgDataType:
    photo: str = None
    video: str = None


@dataclass(slots=True)
class BTNDataType:
    catalog: str
    key: str
    callback: str
    args: dict[any] = None


@dataclass(slots=True)
class KbDataType:
    buttons: list[list[BTNDataType]] | list[list[IB]] = None   # вложенный список с кнопками - один список = один ряд кнопок
    back_callback: str = None        # указываем колбек для кнопки "назад", если она нужна
    back_to_main_menu: bool = False  # указываем True для кнопки "В главное меню", если она нужна


@dataclass(slots=True)
class MessageDataType:
    text: str
    keyboard: KbDataType = None
    media: MediaContentForMsgDataType = MediaContentForMsgDataType()