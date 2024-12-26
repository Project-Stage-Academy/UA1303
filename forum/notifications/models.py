from django.db import models
from users.models import CustomUser


class NotificationType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Preferences for {self.user.email if self.user else 'Unknown User'}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='notification_preferences')
    allowed_notification_types = models.ManyToManyField(NotificationType, related_name='allowed_users')

    def __str__(self):
        return f"Preferences for {self.user.email}"
