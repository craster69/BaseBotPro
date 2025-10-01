# forms.py
from django import forms

class BroadcastForm(forms.Form):
    message = forms.CharField(
        label="Текст сообщения",
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Введите текст рассылки (необязательно, если отправляете фото)...',
            'class': 'form-control'
        }),
        required=False
    )
    photo = forms.ImageField(
        label="Фотография (необязательно)",
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        message = cleaned_data.get('message')
        photo = cleaned_data.get('photo')

        if not message and not photo:
            raise forms.ValidationError("Нужно указать либо текст, либо загрузить фото.")
        return cleaned_data