from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from profiles.models import InvestorProfile, StartupProfile

User = get_user_model()


class NotificationMethod(models.Model):
    """
    Represents available notification delivery methods with user-friendly
    descriptions.

    This model stores different methods for delivering notifications
    (e.g., email, SMS, Telegram) along with a brief description of each method.
    It helps users understand the various notification options available.

    Attributes:
    - name (CharField): The unique name of the notification method.
    - description (TextField): A short and informative description of
      the notification method.

    Example Usage:
    - method = NotificationMethod.objects.create(
            name="Email",
            description="Delivers notifications via email."
      )
    - print(method)
    """

    name = models.CharField(
        max_length=100, unique=True, blank=False, null=False, db_index=True
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return (
            f"Notification method("
            f"name={self.name}, "
            f"description={self.description})"
        )

    class Meta:
        db_table = "notification_methods"
        ordering = ["name"]
        verbose_name = "Notification Method"
        verbose_name_plural = "Notification Methods"


class NotificationCategory(models.Model):
    """
    Represents available notification categories with user-friendly
    descriptions.

    This model stores different categories of notifications
    (e.g., System, Message, Follow) along with a brief description.
    It helps users understand the various notification options available.

    Attributes:
    - name (CharField): The unique name of the notification category.
    - description (TextField): A short and informative description of
      the notification category.

    Example Usage:
    - category = NotificationCategory.objects.create(
          name="Follow",
          description="Informs about follows."
      )
    - print(category)
    """

    name = models.CharField(
        max_length=100, unique=True, blank=False, null=False, db_index=True
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return (
            f"Notification category("
            f"name={self.name}, "
            f"description={self.description})"
        )

    class Meta:
        db_table = "notification_categories"
        ordering = ["name"]
        verbose_name = "Notification Category"
        verbose_name_plural = "Notification Categories"


class NotificationPreference(models.Model):
    """
    Represents a user's preferences for receiving notifications.

    This model allows users to specify which notifications categories
    they wish to receive and how.

    Attributes:
    - user (OneToOneField): The user who owns the notification preferences.
    - allowed_notification_methods (ManyToManyField): The list of
      notification methods choosed by user.
    - allowed_notification_categories (ManyToManyField): The list of
      notification categories the user is interested in.

    Example Usage:
    - preference = NotificationPreference.objects.create(
          user=user_instance,
          allowed_notification_methods=methods_list,
          allowed_notification_categories=categories_list
      )
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    allowed_notification_methods = models.ManyToManyField(
        NotificationMethod, related_name="allowed_methods"
    )
    allowed_notification_categories = models.ManyToManyField(
        NotificationCategory, related_name="allowed_categories"
    )

    def __str__(self):
        return f"Preferences for {self.user.email}"

    class Meta:
        db_table = "notification_preferences"
        ordering = ["user"]
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"


class NotificationQuerySet(models.QuerySet):
    def unread(self):
        """
        Filter notifications that are unread.
        """
        return self.filter(is_read=False)

    def for_investor(self, investor):
        """
        Filter notifications for a specific investor.
        """
        return self.filter(investor=investor)

    def for_startup(self, startup):
        """
        Filter notifications for a specific startup.
        """
        return self.filter(startup=startup)
    

class StartUpNotification(models.Model):
    """
    Represents a notification sent to a startup about an investor's activity.

    Attributes:
        notification_category (NotificationCategory): The category of notification.
        investor (InvestorProfile): The investor related to the notification.
        startup (StartupProfile): The startup that received the notification.
        is_read (bool): Indicates whether the notification has been read.
        created_at (datetime): The date and time the notification was created.

    Related models:
        NotificationCategory: The category of notification.
        InvestorProfile: The investor who triggered the notification.
        StartupProfile: The startup that received the notification.
        Project: The project associated with the notification (if applicable).
    """
    
    notification_category = models.ForeignKey(NotificationCategory, on_delete=models.CASCADE, related_name='notifications')
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='notifications')
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='notifications', db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use the custom QuerySet as the default manager
    objects = NotificationQuerySet.as_manager()

    class Meta:
        verbose_name = "Startup Notification"
        verbose_name_plural = "Startup Notifications"
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['notification_category', 'investor', 'startup'],
                name='unique_notification'
            )
        ]

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    @classmethod
    def mark_all_as_read(cls, user):
        """
        Mark all unread notifications for a specific user as read.
        """
        cls.objects.unread().for_startup(user.startup_profile).update(is_read=True)


class InvestorNotification(models.Model):
    """
    Represents a notification sent to an investor about a startup's activity.

    Attributes:
        notification_category (NotificationCategory): The category of notification.
        investor (InvestorProfile): The investor related to the notification.
        startup (StartupProfile): The startup that received the notification.
        is_read (bool): Indicates whether the notification has been read.
        created_at (datetime): The date and time the notification was created.
        updated_at: The date and time the notification was updated.

    Related models:
        NotificationCategory: The category of notification.
        StartupProfile: The startup who triggered the notification. 
        InvestorProfile: The investor who received the notification.
        Project: The project associated with the notification (if applicable).
    """
    notification_category = models.ForeignKey(NotificationCategory, on_delete=models.CASCADE, related_name='investor_notifications')
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='investor_notifications', db_index=True)
    startup = models.ForeignKey(StartupProfile, on_delete=models.CASCADE, related_name='investor_notifications')
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use the custom QuerySet as the default manager
    objects = NotificationQuerySet.as_manager()

    class Meta:
        verbose_name = "Investor Notification"
        verbose_name_plural = "Investor Notifications"
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['notification_category', 'investor', 'startup'],
                name='unique_investor_notification'
            )
        ]

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    @classmethod
    def mark_all_as_read(cls, user):
        """
        Mark all unread notifications for a specific user as read.
        """
        cls.objects.unread().for_investor(user.investor_profile).update(is_read=True)