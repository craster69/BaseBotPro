from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

import os
import re
import json

from .forms import BroadcastForm
from .tasks import broadcast_message

# --- Broadcast View ---
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
            except (ValueError, TypeError):
                buttons = []

            broadcast_message.delay(user_ids, message_text, photo_path, buttons)
            messages.success(request, "📨 Рассылка поставлена в очередь.")
            return redirect('admin:panel_users_changelist')
    else:
        user_ids = request.GET.getlist('user_id')
        form = BroadcastForm()

    return render(request, 'admin/broadcast_form.html', {
        'form': form,
        'user_ids': user_ids,
    })


# --- Texts Editor ---
BASE_DIR = settings.BASE_DIR
TEXTS_DIR = os.path.join(BASE_DIR, 'bot', 'texts')


def get_files_by_lang(selected_lang=None):
    """Возвращает файлы: все или только для одного языка."""
    if not os.path.exists(TEXTS_DIR):
        os.makedirs(TEXTS_DIR)

    all_langs = sorted([
        d for d in os.listdir(TEXTS_DIR)
        if os.path.isdir(os.path.join(TEXTS_DIR, d))
    ])

    if selected_lang and selected_lang in all_langs:
        # Только один язык
        files_by_lang = {selected_lang: []}
        lang_dir = os.path.join(TEXTS_DIR, selected_lang)
        for filename in sorted(os.listdir(lang_dir)):
            if filename.endswith('.json'):
                filepath = os.path.join(lang_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                    files_by_lang[selected_lang].append({
                        'lang': selected_lang,
                        'filename': filename,
                        'filepath': filepath,
                        'content': content,
                        'raw_content': json.dumps(content, indent=2, ensure_ascii=False),
                    })
                except Exception:
                    continue
    else:
        # Все языки
        files_by_lang = {}
        for lang in all_langs:
            lang_dir = os.path.join(TEXTS_DIR, lang)
            files = []
            for filename in sorted(os.listdir(lang_dir)):
                if filename.endswith('.json'):
                    filepath = os.path.join(lang_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = json.load(f)
                        files.append({
                            'lang': lang,
                            'filename': filename,
                            'filepath': filepath,
                            'content': content,
                            'raw_content': json.dumps(content, indent=2, ensure_ascii=False),
                        })
                    except Exception:
                        continue
            if files:
                files_by_lang[lang] = files

    return files_by_lang, all_langs


@staff_member_required
def edit_texts_view(request):
    selected_lang = request.GET.get('lang', '').strip()

    if request.method == "POST":
        action = request.POST.get('action')
        safe_texts_dir = os.path.abspath(TEXTS_DIR)

        if action == 'delete_file':
            file_path = request.POST.get('file_path')
            if not file_path:
                messages.error(request, "❌ Путь к файлу не указан.")
            else:
                real_path = os.path.abspath(file_path)
                if not real_path.startswith(safe_texts_dir):
                    messages.error(request, "❌ Недопустимый путь к файлу.")
                else:
                    try:
                        os.remove(real_path)
                        messages.success(request, "🗑️ Файл успешно удалён.")
                    except Exception as e:
                        messages.error(request, f"❌ Ошибка удаления: {e}")

        elif action == 'create_lang':
            lang_code = request.POST.get('lang_code', '').strip().lower()
            if not lang_code or not re.match(r'^[a-z]{2,5}$', lang_code):
                messages.error(request, "❌ Код языка: 2–5 латинских букв.")
            else:
                lang_dir = os.path.join(TEXTS_DIR, lang_code)
                if os.path.exists(lang_dir):
                    messages.warning(request, f"⚠️ Язык `{lang_code}` уже существует.")
                else:
                    os.makedirs(lang_dir)
                    messages.success(request, f"✅ Язык `{lang_code}` создан.")
                    selected_lang = lang_code  # автоматически фильтровать на новый язык

        elif action == 'create_file':
            lang_code = request.POST.get('new_file_lang', '').strip()
            filename = request.POST.get('new_filename', '').strip()
            if not lang_code or not filename:
                messages.error(request, "❌ Укажите язык и имя файла.")
            else:
                if not filename.endswith('.json'):
                    filename += '.json'
                if not re.match(r'^[a-zA-Z0-9_\-]+\.json$', filename):
                    messages.error(request, "❌ Имя файла: только буквы, цифры, _ и -.")
                else:
                    lang_dir = os.path.join(TEXTS_DIR, lang_code)
                    if not os.path.exists(lang_dir):
                        messages.error(request, f"❌ Язык `{lang_code}` не существует.")
                    else:
                        filepath = os.path.join(lang_dir, filename)
                        if os.path.exists(filepath):
                            messages.warning(request, f"⚠️ Файл `{filename}` уже существует.")
                        else:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                json.dump({}, f, indent=2, ensure_ascii=False)
                            messages.success(request, f"✅ Файл `{lang_code}/{filename}` создан.")
                            selected_lang = lang_code

        elif action == 'save_file':
            file_path = request.POST.get('file_path')
            new_content = request.POST.get('content', '')
            if not file_path:
                messages.error(request, "❌ Путь к файлу не указан.")
            else:
                real_path = os.path.abspath(file_path)
                if not real_path.startswith(safe_texts_dir):
                    messages.error(request, "❌ Недопустимый путь к файлу.")
                else:
                    try:
                        json.loads(new_content)  # валидация
                        with open(real_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        messages.success(request, "✅ Файл успешно сохранён.")
                    except json.JSONDecodeError as e:
                        messages.error(request, f"❌ Невалидный JSON: {e}")
                    except Exception as e:
                        messages.error(request, f"❌ Ошибка записи: {e}")

    # Обновляем данные после любого действия
    files_by_lang, all_langs = get_files_by_lang(selected_lang)
    return render(request, 'admin/edit_texts.html', {
        'text_files': files_by_lang,
        'existing_langs': all_langs,
        'selected_lang': selected_lang,
    })