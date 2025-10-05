from django.contrib import admin
from django import forms
from django.http import HttpResponse

import csv

from panel.models import Users

from bot.utils.base_utils import get_languages

class UsersAdminForm(forms.ModelForm):
    language_code = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'vTextField'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        languages = get_languages()
        self.fields['language_code'].choices = [
            (lang, lang.upper()) for lang in languages
        ]

    class Meta:
        model = Users
        fields = '__all__'

class UsersAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'name', 'role', 'language_code', 'date_joined')
    list_filter = ('role', 'language_code', 'date_joined')
    search_fields = ('tg_id', 'name')
    list_editable = ('role', 'language_code')
    list_per_page = 30
    fieldsets = (
        ('ℹ️ Основная информация', {'fields': ('tg_id', 'name')}),
        ('⚙️ Настройки', {'fields': ('role', 'language_code')}),
    )
    readonly_fields = ('date_joined',)
    actions = ['export_as_csv', 'send_msg_users']

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        writer = csv.writer(response)
        writer.writerow(['Telegram ID', 'Имя', 'Роль', 'Язык', 'Дата регистрации'])
        for user in queryset:
            writer.writerow([
                user.tg_id,
                user.name,
                user.get_role_display(),
                user.language_code,
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else ''
            ])
        return response

    export_as_csv.short_description = "Выгрузить таблицу в CSV"

    def send_msg_users(self, request, queryset):
        user_ids = queryset.values_list('tg_id', flat=True)
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        url = reverse('broadcast') + '?' + '&'.join([f'user_id={uid}' for uid in user_ids])
        return HttpResponseRedirect(url)

    send_msg_users.short_description = "Запустить рассылку"