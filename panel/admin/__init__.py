from django.contrib import admin
from .users import UsersAdmin
from panel.models import Users

admin.site.register(Users, UsersAdmin)