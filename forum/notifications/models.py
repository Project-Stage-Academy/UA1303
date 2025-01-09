from django.db import models
from django.contrib.auth import get_user_model
from profiles.models import InvestorProfile, StartupProfile

User = get_user_model()

class NotificationType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    allowed_notification_types = models.ManyToManyField(NotificationType, related_name='allowed_users')

    def __str__(self):
        return f"Preferences for {self.user.username}"
    

class StartUpNotification(models.Model):
    """
    Represents a notification sent to a startup about an investor's activity.

    Attributes:
        notification_type (NotificationType): The type of notification.
        investor (InvestorProfile): The investor related to the notification.
        startup (StartupProfile): The startup that received the notification.
        is_read (bool): Indicates whether the notification has been read.
        created_at (datetime): The date and time the notification was created.

    Related models:
        NotificationType: The type of notification.
        InvestorProfile: The investor who triggered the notification.
        StartupProfile: The startup that received the notification.
        Project: The project associated with the notification (if applicable).
    """
    
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, related_name='notifications')
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='notifications')
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='notifications', db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Startup Notification"
        verbose_name_plural = "Startup Notifications"
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['notification_type', 'investor', 'startup'],
                name='unique_notification'
            )
        ]

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()