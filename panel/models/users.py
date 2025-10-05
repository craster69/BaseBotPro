from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    BigIntegerField
)
from panel.enums import UserRoleEnum


class Users(Model):
    tg_id = BigIntegerField(
        unique=True,
        db_index=True,
    )
    name = CharField(
        max_length=32,
        null=True,
        blank=True,
    )
    role = CharField(
        max_length=15,
        choices=UserRoleEnum,
        default=UserRoleEnum.USER, 
    )
    language_code = CharField(
        max_length=2,
        null=True,
        blank=True,
    )
    date_joined = DateTimeField(
        auto_now_add=True,
    )

    def __str__(self) -> str:
        return f'ID_{self.tg_id}'

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']