from django.test import TestCase
from django.contrib.auth.models import User
from .models import NotificationType, NotificationPreference
from .serializers import (
    NotificationTypeSerializer,
    NotificationPreferenceSerializer,
    NotificationPreferenceUpdateSerializer
)


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.notification_type = NotificationType.objects.create(
            name="email", description="Email notifications"
        )
        self.notification_preference, created = NotificationPreference.objects.get_or_create(user=self.user)
        self.notification_preference.allowed_notification_types.add(self.notification_type)

    def test_notification_type_creation(self):
        self.assertEqual(self.notification_type.name, "email")
        self.assertEqual(self.notification_type.description, "Email notifications")

    def test_notification_preference_creation(self):
        self.assertEqual(self.notification_preference.user.username, "testuser")
        self.assertEqual(self.notification_preference.allowed_notification_types.count(), 1)
        self.assertEqual(self.notification_preference.allowed_notification_types.first().name, "email")


class NotificationSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.notification_type = NotificationType.objects.create(
            name="email", description="Email notifications"
        )
        self.notification_preference = NotificationPreference.objects.create(user=self.user)
        self.notification_preference.allowed_notification_types.add(self.notification_type)

    def test_notification_type_serializer(self):
        serializer = NotificationTypeSerializer(instance=self.notification_type)
        self.assertEqual(serializer.data["name"], "email")
        self.assertEqual(serializer.data["description"], "Email notifications")

    def test_notification_preference_serializer(self):
        serializer = NotificationPreferenceSerializer(instance=self.notification_preference)
        self.assertEqual(serializer.data["allowed_notification_types"][0]["name"], "email")

    def test_notification_preference_update_serializer(self):
        serializer = NotificationPreferenceUpdateSerializer(data={
            "allowed_notification_types": [self.notification_type.id]
        })
        self.assertTrue(serializer.is_valid())
