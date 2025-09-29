from django import forms

class BroadcastForm(forms.Form):
    message = forms.CharField(
        label="Текст сообщения",
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Введите текст рассылки...',
            'class': 'form-control'
        }),
        required=True
    )