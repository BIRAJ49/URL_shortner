import hashlib

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


KEY_LENGTH = 10


def sha256_short_key(value):
    return hashlib.sha256(str(value).encode()).hexdigest()[:KEY_LENGTH]


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
            self.key = self.generate_key()
            super().save(update_fields=['key'])

    def generate_key(self):
        for counter in range(100):
            seed = f'{self.pk}:{self.owner_id}:{self.long_url}:{counter}'
            key = sha256_short_key(seed)
            if not ShortURL.objects.filter(key=key).exclude(pk=self.pk).exists():
                return key
        raise ValueError('Could not generate a unique short key.')

    def is_expired(self):
        return bool(self.expires_at and self.expires_at <= timezone.now())

    def get_short_path(self):
        return reverse('shortener:redirect', kwargs={'key': self.key})

    def __str__(self):
        return f'{self.key} -> {self.long_url}'
