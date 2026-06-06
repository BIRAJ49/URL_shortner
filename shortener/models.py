import string

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


BASE62_ALPHABET = string.digits + string.ascii_letters


def base62_encode(number):
    if number == 0:
        return BASE62_ALPHABET[0]

    encoded = []
    base = len(BASE62_ALPHABET)
    while number:
        number, remainder = divmod(number, base)
        encoded.append(BASE62_ALPHABET[remainder])
    return ''.join(reversed(encoded))


class ShortURL(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='short_urls',
    )
    long_url = models.URLField(max_length=2048)
    key = models.SlugField(max_length=32, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    click_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        needs_key = not self.key
        super().save(*args, **kwargs)
        if needs_key:
            self.key = base62_encode(self.pk)
            super().save(update_fields=['key'])

    def is_expired(self):
        return self.expires_at is not None and self.expires_at <= timezone.now()

    def get_short_path(self):
        return reverse('shortener:redirect', kwargs={'key': self.key})

    def __str__(self):
        return f'{self.key} -> {self.long_url}'
