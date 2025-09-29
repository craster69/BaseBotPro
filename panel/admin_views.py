from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .forms import BroadcastForm
from .tasks import broadcast_message

@staff_member_required
def broadcast_view(request):
    if request.method == "POST":
        form = BroadcastForm(request.POST)
        if form.is_valid():
            message_text = form.cleaned_data['message']
            user_ids = request.POST.getlist('user_id')
            broadcast_message.delay(user_ids, message_text)
            messages.success(request, "📨 Рассылка поставлена в очередь.")
            return redirect('admin:panel_users_changelist')
    else:
        user_ids = request.GET.getlist('user_id')
        form = BroadcastForm()
    
    return render(request, 'admin/broadcast_form.html', {
        'form': form,
        'user_ids': request.GET.getlist('user_id') or request.POST.getlist('user_id'),
    })