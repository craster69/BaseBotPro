from django.db.models import TextChoices


class UserRoleEnum(TextChoices):
    SUPPORT = 'support', 'Тех. поддержка'
    OWNER = 'owner', 'Владелец'
    ADMIN = 'admin', 'Администратор'
    USER = 'user', 'Пользователь'