from django.urls import path
from . import admin_views

app_name = 'panel'

urlpatterns = [
    path('admin/broadcast/', admin_views.broadcast_view, name='broadcast'),
    path('admin/edit_texts/', admin_views.edit_texts_view, name='edit_texts')
]