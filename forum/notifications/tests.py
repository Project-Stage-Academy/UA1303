from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import (
    NotificationType,
    NotificationCategory,
    NotificationPreference
)
from .serializers import (
    NotificationTypeSerializer,
    NotificationCategorySerializer,
    NotificationPreferenceSerializer,
    NotificationPreferenceUpdateSerializer
)


User = get_user_model()


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@user.com', password='password')
        self.notification_type = NotificationType.objects.create(
            name="email", description="Email notifications"
        )
        self.notification_category = NotificationCategory.objects.create(
            name="Message", description="You have message from some user"
        )
        self.notification_preference, created = NotificationPreference.objects.get_or_create(user=self.user)
        self.notification_preference.allowed_notification_types.add(self.notification_type)
        self.notification_preference.allowed_notification_categories.add(self.notification_category)

    def test_notification_type_creation(self):
        self.assertEqual(self.notification_type.name, "email")
        self.assertEqual(self.notification_category.name, "Message")
        self.assertEqual(self.notification_type.description, "Email notifications")
        self.assertEqual(self.notification_category.description, "You have message from some user")

    def test_notification_preference_creation(self):
        self.assertEqual(self.notification_preference.user.email, "test@user.com")
        self.assertEqual(self.notification_preference.allowed_notification_types.count(), 1)
        self.assertEqual(self.notification_preference.allowed_notification_types.first().name, "email")
        self.assertEqual(self.notification_preference.allowed_notification_categories.count(), 1)
        self.assertEqual(self.notification_preference.allowed_notification_categories.first().name, "Message")


class NotificationSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@user.com', password='password')
        self.notification_type = NotificationType.objects.create(
            name="email", description="Email notifications"
        )
        self.notification_category = NotificationCategory.objects.create(
            name="Message", description="You have message from some user"
        )
        self.notification_preference = NotificationPreference.objects.create(user=self.user)
        self.notification_preference.allowed_notification_types.add(self.notification_type)
        self.notification_preference.allowed_notification_categories.add(self.notification_category)

    def test_notification_type_serializer(self):
        serializer = NotificationTypeSerializer(instance=self.notification_type)
        self.assertEqual(serializer.data["name"], "email")
        self.assertEqual(serializer.data["description"], "Email notifications")

    def test_notification_category_serializer(self):
        serializer = NotificationCategorySerializer(instance=self.notification_category)
        self.assertEqual(serializer.data["name"], "Message")
        self.assertEqual(serializer.data["description"], "You have message from some user")

    def test_notification_preference_serializer(self):
        serializer = NotificationPreferenceSerializer(instance=self.notification_preference)
        self.assertEqual(serializer.data["allowed_notification_types"][0]["name"], "email")
        self.assertEqual(serializer.data["allowed_notification_categories"][0]["name"], "Message")

    def test_notification_preference_update_serializer(self):
        serializer = NotificationPreferenceUpdateSerializer(data={
            "allowed_notification_types": [self.notification_type.id],
            "allowed_notification_categories": [self.notification_category.id]
        })
        self.assertTrue(serializer.is_valid())
