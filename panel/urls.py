from django.urls import path
from . import admin_views

urlpatterns = [
    path('admin/broadcast/', admin_views.broadcast_view, name='broadcast'),
]