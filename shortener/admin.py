from django.contrib import admin

from .models import ShortURL


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ('key', 'owner', 'long_url', 'click_count', 'created_at', 'expires_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('key', 'long_url', 'owner__username')
    readonly_fields = ('created_at', 'updated_at', 'click_count')
