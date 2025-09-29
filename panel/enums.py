from django.db.models import TextChoices


class LanguageEnum(TextChoices):
    """языки в боте"""
    RU = 'ru', 'Русский'
    EN = 'en', 'Английский'


class UserRoleEnum(TextChoices):
    SUPPORT = 'support', 'Тех. поддержка'
    OWNER = 'owner', 'Владелец'
    ADMIN = 'admin', 'Администратор'
    USER = 'user', 'Пользователь'