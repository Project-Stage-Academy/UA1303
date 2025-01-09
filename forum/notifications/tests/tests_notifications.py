from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from profiles.models import StartupProfile
from projects.models import Project, Description
from ..models import NotificationForUpdates
from rest_framework.test import APIClient, APITestCase
from decimal import Decimal

User = get_user_model()

def create_db_data(cls):
    """Helper method to create commonly used database data"""
    create_user(cls)
    create_startup_profile(cls)
    create_project(cls)

def create_user(cls):
    """Helper method to create a user"""
    cls.user = User.objects.create_user(
        email="test@user.com",
        password="Password!+",
        first_name="Test",
        last_name="User",
    )

def create_startup_profile(cls):
    """Helper method to create a startup profile"""
    cls.startup_profile = StartupProfile.objects.create(
        user=cls.user,
        company_name="Test Startup",
        industry="Technology",
        size="Small",
        country="USA",
        city="New York",
        zip_code="10001",
        address="123 Test Street",
        phone="+1234567890",
        email="startup@example.com",
        description="A test startup",
        is_public=True,
    )

def create_project(cls):
    """Helper method to create a project"""
    cls.project = Project.objects.create(
        startup=cls.startup_profile,
        title="Test Project",
        funding_goal=Decimal("10000.00"),
        is_published=True,
        is_completed=False,
    )

    Description.objects.create(
        project=cls.project,
        description="A test project description",
    )


class TestUnitNotificationForUpdatesModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        create_db_data(cls)

    def test_notification_creation(self):
        notification = NotificationForUpdates.objects.create(
            user=self.user,
            notification_type="investor",
            message="Test notification",
            startup_profile=self.startup_profile,
        )
        self.assertTrue(
            NotificationForUpdates.objects.filter(id=notification.id).exists(),
        )

    def test_notification_str_method(self):
        notification = NotificationForUpdates.objects.create(
            user=self.user,
            notification_type="investor",
            message="Test notification",
            startup_profile=self.startup_profile,
        )
        expected_str = f"{self.user.email} - Test notification"
        self.assertEqual(
            str(notification), expected_str,
        )

    def test_notification_deletion(self):
        notification = NotificationForUpdates.objects.create(
            user=self.user,
            notification_type="investor",
            message="Test notification",
            startup_profile=self.startup_profile,
        )
        notification.delete()
        self.assertFalse(
            NotificationForUpdates.objects.filter(id=notification.id).exists(),
            "Notification was not deleted.",
        )


class TestNotificationSignals(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        create_db_data(cls)

    def test_notification_on_startup_profile_update(self):
        self.startup_profile.company_name = "Updated Startup Name"
        self.startup_profile.save()

        notification = NotificationForUpdates.objects.filter(
            user=self.user, startup_profile=self.startup_profile
        ).first()
        self.assertIsNotNone(
            notification, "Notification was not created for profile update."
        )
        self.assertEqual(
            notification.message,
            f"{self.startup_profile.company_name} has updated their profile.",
            "Notification message is incorrect.",
        )

    def test_notification_on_new_project_post(self):
        new_project = Project.objects.create(
            startup=self.startup_profile,
            title="New Project",
            funding_goal=Decimal("20000.00"),
            is_published=True,
            is_completed=False,
        )

        Description.objects.create(
            project=new_project,
            description="A new project description",
        )
        notification = NotificationForUpdates.objects.filter(
            user=self.user, project=new_project
        ).first()
        self.assertIsNotNone(
            notification, "Notification was not created for new project post."
        )
        self.assertEqual(
            notification.message,
            f"{self.startup_profile.company_name} has posted a new project: {new_project.title}.",
            "Notification message is incorrect.",
        )


class TestNotificationAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        create_db_data(cls)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        NotificationForUpdates.objects.filter(user=self.user).delete()

    def test_fetch_notifications(self):
        NotificationForUpdates.objects.create(
            user=self.user,
            notification_type="investor",
            message="Test notification",
            startup_profile=self.startup_profile,
        )
        url = reverse("notifications:investor_notifications/")
        response = self.client.get(url)
        self.assertEqual(
            response.status_code, 200, "API endpoint returned an error."
        )
        self.assertEqual(
            len(response.data), 1, "Incorrect number of notifications returned."
        )
        self.assertEqual(
            response.data[0]["message"],
            "Test notification",
            "Notification message is incorrect.",
        )