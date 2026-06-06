from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import ShortURL


RESERVED_KEYS = {
    'admin',
    'accounts',
    'create',
    'delete',
    'edit',
    'qr',
    'register',
    'urls',
}


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ShortURLForm(forms.ModelForm):
    custom_key = forms.SlugField(
        max_length=32,
        required=False,
        help_text='Optional. Use letters, numbers, underscores, or hyphens.',
    )

    class Meta:
        model = ShortURL
        fields = ['long_url', 'custom_key', 'expires_at']
        widgets = {
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        help_texts = {
            'expires_at': 'Optional. Leave blank for no expiration.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['custom_key'].initial = self.instance.key

    def clean_custom_key(self):
        key = self.cleaned_data.get('custom_key', '').strip()
        if not key:
            return key

        if key.lower() in RESERVED_KEYS:
            raise ValidationError('This short key is reserved.')

        queryset = ShortURL.objects.filter(key=key)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError('This short key is already taken.')

        return key

    def clean_expires_at(self):
        expires_at = self.cleaned_data.get('expires_at')
        if expires_at and expires_at <= timezone.now():
            raise ValidationError('Expiration time must be in the future.')
        return expires_at

    def save(self, commit=True):
        instance = super().save(commit=False)
        custom_key = self.cleaned_data.get('custom_key')
        if custom_key:
            instance.key = custom_key
        elif instance.pk is None:
            instance.key = ''

        if commit:
            instance.save()
        return instance
