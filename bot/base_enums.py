from enum import Enum


class ParseModeEnum(str, Enum):
    """parse_mode для бота"""
    HTML = 'html'
    MARKDOWN = 'markdown'


class RunTypeEnum(str, Enum):
    """тип запуска бота"""
    POLLING = 'polling'
    WEBHOOK = 'webhook'


class EnvEnum(str, Enum):
    """поля из .env файла"""
    TOKEN_TG_BOT = 'TOKEN_TG_BOT'
    DB_HOST = 'DB_HOST'
    DB_PORT = 'DB_PORT'
    DB_USER = 'DB_USER'
    DB_PASSWORD = 'DB_PASSWORD'
    DB_NAME = 'DB_NAME'
    REDIS_HOST = 'REDIS_HOST'
    REDIS_PORT = 'REDIS_PORT'
    WEBHOOK_URL = 'WEBHOOK_URL'
    MODERATOR_CHAT_ID = 'MODERATOR_CHAT_ID'


class LanguageEnum(str, Enum):
    """языки в боте"""
    RU = 'ru'
    EN = 'en'


class MainCallbackEnum(str, Enum):
    """главные кнопки в боте"""
    BACK = 'back'
    BACK_TO_MAIN_MENU = 'back_to_main_menu'
    PORTFOLIO = 'portfolio'
    ABOUT_US = 'about_us'
    ADDING_ACCOUNTS = 'adding_accounts'
    HELP = 'help'
    ACCOUNTS_MANAGEMENT = 'accounts_management'
    CHOOSE_LANGUAGE = 'choose_language'


class OtherCallbackEnum(str, Enum):
    """список оставшихся callback`ов"""
    CHOOSE_LANGUAGE_ = 'choose_language_'


class UserRoleEnum(str, Enum):
    SUPPORT = 'support'
    OWNER = 'owner'
    ADMIN = 'admin'
    USER = 'user'
