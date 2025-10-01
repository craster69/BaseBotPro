from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import os

import json

from .forms import BroadcastForm
from .tasks import broadcast_message


@staff_member_required
def broadcast_view(request):
    if request.method == "POST":
        form = BroadcastForm(request.POST, request.FILES)
        user_ids = request.POST.getlist('user_id')
        if form.is_valid():
            message_text = form.cleaned_data['message']
            photo = form.cleaned_data.get('photo')
            photo_path = None
            
            if photo:
                filename = default_storage.save(f"temp_files/{photo.name}", ContentFile(photo.read()))
                photo_path = default_storage.path(filename)
            
            buttons_json = request.POST.get('buttons_json', '[]')
            try:
                buttons = json.loads(buttons_json)
            except:
                buttons = []
            
            broadcast_message.delay(user_ids, message_text, photo_path, buttons)
            messages.success(request, "📨 Рассылка поставлена в очередь.")
            return redirect('admin:panel_users_changelist')
    else:
        user_ids = request.GET.getlist('user_id')
        form = BroadcastForm()
    
    return render(request, 'admin/broadcast_form.html', {
        'form': form,
        'user_ids': request.GET.getlist('user_id') or request.POST.getlist('user_id'),
    })