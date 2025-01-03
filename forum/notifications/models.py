from django.db import models
from django.conf import settings


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
