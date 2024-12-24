from django.contrib import admin

from .models import NotificationType, NotificationPreference


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user']
    filter_horizontal = ['allowed_notification_types']

