from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
import jwt
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, timedelta

from ..models import NotificationMethod, NotificationCategory, NotificationPreference
from ..serializers import (
    NotificationMethodSerializer,
    NotificationCategorySerializer,
    NotificationPreferenceSerializer,
    NotificationPreferenceUpdateSerializer,
)
from ..views import ROLE_CATEGORIES

User = get_user_model()


def send_get_request_with_role(self, user, role, url):
    """
    Helper method to send get request with authorization using the role.
    Returns response json
    """
    auth_header = generate_auth_header(user, role)
    return self.client.get(url, **auth_header).json()


def create_db_data(cls):
    """Helper method to create common used set of database data"""
    create_categories(cls)
    create_methods(cls)
    create_user(cls)


def create_user(cls):
    """Helper method to create user and relevant items"""
    cls.user = User.objects.create_user(
        email="test@user.com", password="password", role=3
    )


def create_categories(cls):
    """Helper method to create categories"""
    cls.followCategory = NotificationCategory.objects.get(name="follow")
    cls.messageCategory = NotificationCategory.objects.create(
        name="message", description="Informs about messages"
    )
    cls.projectchangesCategory = NotificationCategory.objects.create(
        name="project_changes", description="Informs about changes in some project"
    )
    cls.subscriptionCategory = NotificationCategory.objects.create(
        name="subscription", description="Informs about subscription on some project"
    )


def create_methods(cls):
    """Helper method to create methods"""
    cls.popupMethod = NotificationMethod.objects.create(
        name="pop-up", description="Notification via pop-up"
    )
    cls.telegramMethod = NotificationMethod.objects.create(
        name="telegram", description="Notification via telegram"
    )


def generate_auth_header(user, role):
    """Helper method to create header with authentication token"""
    token = generate_jwt_token(user, role)
    auth_header = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
    return auth_header


def generate_jwt_token(user, role):
    """Helper method to create JWT token based on user and role"""
    payload = {
        "token_type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=5),
        "iat": datetime.utcnow(),
        "jti": "test-jwt-id",
        "user_id": user.user_id,
        "role": role,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


class TestUnitNotificationMethodModel(TestCase):
    """
    Tests the NotificationMethod model's unit functionality,
    ensuring that methods are correctly created and stored in the database.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_methods(cls)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_iscreated_popup(self):
        actual = NotificationMethod.objects.filter(name="pop-up").exists()
        self.assertTrue(actual, "Detail: There is no Pop-Up method in the table.")

    def test_iscreated_telegram(self):
        actual = NotificationMethod.objects.filter(name="telegram").exists()
        self.assertTrue(actual, "Detail: There is no Telegram method in the table.")

    def test_description_popup(self):
        actual = NotificationMethod.objects.get(name="pop-up").description
        self.assertEqual(
            actual, "Notification via pop-up", "Detail: Wrong description for Pop-Up"
        )

    def test_description_telegram(self):
        actual = NotificationMethod.objects.get(name="telegram").description
        self.assertEqual(
            actual,
            "Notification via telegram",
            "Detail: Wrong description for Telegram",
        )

    def test_delete_object(self):
        NotificationMethod.objects.get(name="pop-up").delete()
        actual = NotificationMethod.objects.filter(name="pop-up").exists()
        self.assertFalse(actual, "Detail: There is a Pop-Up method in the table.")

    def test_str_method(self):
        smsMethod = NotificationMethod.objects.create(
            name="sms", description="Notification via sms"
        )
        expected = "Notification method(name=sms, description=Notification via sms)"
        self.assertEqual(
            str(smsMethod), expected, "Details: __str__ returns incorrect format."
        )


class TestUnitNotificationCategoryModel(TestCase):
    """
    Tests the NotificationCtegory model's unit functionality,
    ensuring that categories are correctly created and stored in the database.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_categories(cls)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_iscreated_follow(self):
        actual = NotificationCategory.objects.filter(name="follow").exists()
        self.assertTrue(actual, "Detail: There is no Follow category in the table.")

    def test_iscreated_message(self):
        actual = NotificationCategory.objects.filter(name="message").exists()
        self.assertTrue(actual, "Detail: There is no Message category in the table.")

    def test_description_follow(self):
        actual = NotificationCategory.objects.get(name="follow").description
        self.assertEqual(
            actual, "A new investor is following your startup.", "Detail: Wrong description for Follow."
        )

    def test_description_message(self):
        actual = NotificationCategory.objects.get(name="message").description
        self.assertEqual(
            actual, "Informs about messages", "Detail: Wrong description for Message"
        )

    def test_delete_object(self):
        NotificationCategory.objects.get(name="message").delete()
        actual = NotificationCategory.objects.filter(name="message").exists()
        self.assertFalse(actual, "Detail: There is a Message category in the table.")

    def test_str_category(self):
        followCategory = NotificationCategory.objects.create(
            name="system", description="Informs about system"
        )
        expected = (
            "Notification category(name=system, description=Informs about system)"
        )
        self.assertEqual(
            str(followCategory), expected, "Details: __str__ returns incorrect format."
        )


class TestUnitNotificationPreferenceModel(TestCase):
    """
    Tests the NotificationPreference model's unit functionality,
    ensuring that preferences are correctly created and stored in the database.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_db_data(cls)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_create_preference(self):
        self.notification_preference = NotificationPreference.objects.create(
            user=self.user
        )
        actual = NotificationPreference.objects.filter(user=self.user).exists()
        self.assertTrue(
            actual, "Detail: There is no preference for this user in the table."
        )

    def test_add_method(self):
        self.notification_preference = NotificationPreference.objects.create(
            user=self.user
        )
        self.notification_preference.allowed_notification_methods.add(
            self.telegramMethod
        )
        actual = self.notification_preference.allowed_notification_methods.first().name
        self.assertEqual(
            actual, "telegram", "Detail: There is no telegram method for this user."
        )

    def test_add_category(self):
        self.notification_preference = NotificationPreference.objects.create(
            user=self.user
        )
        self.notification_preference.allowed_notification_categories.add(
            self.followCategory
        )
        actual = (
            self.notification_preference.allowed_notification_categories.first().name
        )
        self.assertEqual(
            actual, "follow", "Detail: There is no follow category for this user."
        )


class TestUnitNotificationMethodSerializer(TestCase):
    """
    Tests the NotificationMethodSerializer unit functionality,
    ensuring that methods are correctly serializing.
    """

    def setUp(self):
        self.valid_data = {"name": "pop-up", "description": "Notification via pop-up"}
        self.invalid_data = {"name": "", "description": "Notification via invalid name"}
        self.notification_method = NotificationMethod.objects.create(
            name="telegram", description="Notification via telegram"
        )

    def test_valid_data(self):
        serializer = NotificationMethodSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["name"],
            self.valid_data["name"],
            "Detail: The expected name is different from the obtained one.",
        )
        self.assertEqual(
            serializer.validated_data["description"],
            self.valid_data["description"],
            "Detail: The expected description is different from the obtained one.",
        )

    def test_invalid_data(self):
        serializer = NotificationMethodSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn(
            "name", serializer.errors, "Detail: Expected validation error for 'name'."
        )

    def test_serialized_data(self):
        serializer = NotificationMethodSerializer(instance=self.notification_method)
        expected = {
            "id": self.notification_method.id,
            "name": self.notification_method.name,
            "description": self.notification_method.description,
        }
        self.assertEqual(
            serializer.data,
            expected,
            "Detail: The expected result is different from the obtained one.",
        )


class TestUnitNotificationCategorySerializer(TestCase):
    """
    Tests the NotificationCategorySerializer unit functionality,
    ensuring that categories are correctly serializing.
    """

    def setUp(self):
        self.valid_data = {"name": "investment", "description": "Somebody invested in your project."}
        self.invalid_data = {"name": "", "description": "Informs about something"}
        self.notification_category = NotificationCategory.objects.create(
            name="message", description="Informs about message"
        )

    def test_valid_data(self):
        serializer = NotificationCategorySerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["name"],
            self.valid_data["name"],
            "Detail: The expected name is different from the obtained one.",
        )
        self.assertEqual(
            serializer.validated_data["description"],
            self.valid_data["description"],
            "Detail: The expected description is different from the obtained one.",
        )

    def test_invalid_data(self):
        serializer = NotificationCategorySerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn(
            "name", serializer.errors, "Detail: Expected validation error for 'name'."
        )

    def test_serialized_data(self):
        serializer = NotificationCategorySerializer(instance=self.notification_category)
        expected = {
            "id": self.notification_category.id,
            "name": self.notification_category.name,
            "description": self.notification_category.description,
        }
        self.assertEqual(
            serializer.data,
            expected,
            "Detail: The expected result is different from the obtained one.",
        )


class TestUnitNotificationPreferenceSerializer(TestCase):
    """
    Tests the NotificationPreferenceSerializer unit functionality,
    ensuring that preferences are correctly serializing.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_db_data(cls)
        cls.notification_preference = NotificationPreference.objects.get_or_create(
            user=cls.user
        )[0]
        cls.notification_preference.allowed_notification_categories.add(
            cls.followCategory
        )
        cls.notification_preference.allowed_notification_methods.add(cls.popupMethod)
        cls.serializer = NotificationPreferenceSerializer(
            instance=cls.notification_preference
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_serialized_preference_method_name(self):
        self.assertEqual(
            self.serializer.data["allowed_notification_methods"][0]["name"],
            "pop-up",
            "Details: Name of method before and after serilizing does not match.",
        )

    def test_serialized_preference_category_name(self):
        self.assertEqual(
            self.serializer.data["allowed_notification_categories"][0]["name"],
            "follow",
            "Details: Name of category before and after serilizing does not match.",
        )

    def test_serialized_preference_method_description(self):
        self.assertEqual(
            self.serializer.data["allowed_notification_methods"][0]["description"],
            "Notification via pop-up",
            "Details: Description of method before and after serilizing does not match.",
        )

    def test_serialized_preference_category_description(self):
        self.assertEqual(
            self.serializer.data["allowed_notification_categories"][0]["description"],
            "A new investor is following your startup.",
            "Details: Description of category before and after serilizing does not match.",
        )

    def test_notification_preference_update_serializer(self):
        serializer = NotificationPreferenceUpdateSerializer(
            data={
                "allowed_notification_methods": [self.popupMethod.id],
                "allowed_notification_categories": [self.followCategory.id],
            }
        )
        self.assertTrue(serializer.is_valid(), "Details: Serializer is not valid.")


class TestIntegrationNotificationCategorySerializer(TestCase):
    """
    Tests NotificationCategorySerializer in integration with models.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = {"name": "new-category", "description": "New description"}
        cls.serializer = NotificationCategorySerializer(data=cls.data)
        if cls.serializer.is_valid():
            cls.category = cls.serializer.save()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_correctness_of_name_serializing(self):
        self.assertEqual(
            self.category.name,
            self.data["name"],
            "Details: Name of category before and after serilizing does not match.",
        )

    def test_correctness_of_description_serializing(self):
        self.assertEqual(
            self.category.description,
            self.data["description"],
            "Details: Description of category before and after serilizing does not match.",
        )


class TestIntegrationNotificationMethodSerializer(TestCase):
    """
    Tests NotificationMethodSerializer in integration with models.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = {"name": "new-method", "description": "New description"}
        cls.serializer = NotificationMethodSerializer(data=cls.data)
        if cls.serializer.is_valid():
            cls.method = cls.serializer.save()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_correctness_of_name_serializing(self):
        self.assertEqual(
            self.method.name,
            self.data["name"],
            "Details: Name of method before and after serilizing does not match.",
        )

    def test_correctness_of_description_serializing(self):
        self.assertEqual(
            self.method.description,
            self.data["description"],
            "Details: Description of method before and after serilizing does not match.",
        )


class TestIntegrationNotificationPreferenceSerializer(TestCase):
    """
    Tests NotificationPreferenceSerializer in integration with models.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_db_data(cls)
        cls.notification_preference = NotificationPreference.objects.get_or_create(
            user=cls.user
        )[0]
        cls.notification_preference.allowed_notification_categories.add(
            cls.followCategory
        )
        cls.notification_preference.allowed_notification_methods.add(cls.popupMethod)
        cls.serializer = NotificationPreferenceSerializer(
            instance=cls.notification_preference
        )
        cls.preference = NotificationPreference.objects.get(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_correctness_of_user_serializing(self):
        actual = self.preference.user
        self.assertEqual(
            actual,
            self.user,
            "Details: Provided user and user from model are not the same.",
        )

    def test_correctness_of_allowed_methods_serializing(self):
        actual = self.preference.allowed_notification_methods
        self.assertEqual(
            actual,
            self.notification_preference.allowed_notification_methods,
            "Details: Different set of methods before serilizing and from serialized model.",
        )

    def test_correctness_of_allowed_categories_serializing(self):
        actual = self.preference.allowed_notification_categories
        self.assertEqual(
            actual,
            self.notification_preference.allowed_notification_categories,
            "Details: Different set of categories before serilizing and from serialized model.",
        )


class TestComponentNotificationCategoryEndpoint(APITestCase):
    """
    Tests NotificationCategory Endpoint like a component.
    Ensures that response containes categories related to current
    user's role.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_user(cls)
        create_categories(cls)
        cls.url = reverse("notifications:notification_categories")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def verify_user_categories(self, role):
        response_json = send_get_request_with_role(self, self.user, role, self.url)
        response_categories = [category["name"] for category in response_json]
        actual = all(
            response_category in ROLE_CATEGORIES.get(role, [])
            for response_category in response_categories
        )
        self.assertTrue(
            actual,
            f"Details: Some categories in the response are not related to role {role}.",
        )

    def test_show_categories_startup(self):
        self.verify_user_categories(role=1)

    def test_show_categories_investor(self):
        self.verify_user_categories(role=2)

    def test_show_categories_not_set_for_role(self):
        self.verify_user_categories(role=333)


class TestComponentNotificationPreferenceEndpoint(APITestCase):
    """
    Tests returned categories in NotificationPreference Endpoint component.
    Ensures that response containes categories related to current
    user's role.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_db_data(cls)
        cls.preference = NotificationPreference.objects.get_or_create(user=cls.user)[0]
        cls.preference.allowed_notification_methods.add(cls.telegramMethod)
        cls.preference.allowed_notification_methods.add(cls.popupMethod)
        cls.preference.allowed_notification_categories.add(cls.followCategory)
        cls.preference.allowed_notification_categories.add(cls.subscriptionCategory)
        cls.preference.allowed_notification_categories.add(cls.projectchangesCategory)
        cls.preference.allowed_notification_categories.add(cls.messageCategory)
        cls.url = reverse("notifications:user_notification_preferences")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def verify_user_preference(self, role):
        """
        Helper method to verify user preferences based on the role.
        """
        response_json = send_get_request_with_role(self, self.user, role, self.url)
        response_categories = response_json["allowed_notification_categories"]
        response_category_names = [category["name"] for category in response_categories]
        actual = all(
            response_category in ROLE_CATEGORIES.get(role, [])
            for response_category in response_category_names
        )
        self.assertTrue(
            actual,
            f"Details: Some categories in the response are not related to role {role}.",
        )

    def test_get_user_preference(self):
        role = 1
        response_json = send_get_request_with_role(self, self.user, role, self.url)
        response_user = response_json["user"]
        self.assertEqual(
            response_user,
            self.user.email,
            "Details: Current response must contain current user.",
        )

    def test_user_startup_preference(self):
        self.verify_user_preference(role=1)

    def test_user_investor_preference(self):
        self.verify_user_preference(role=2)
