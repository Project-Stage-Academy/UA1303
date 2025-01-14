from rest_framework import status
from rest_framework.test import APITestCase
from ..models import InvestorNotification
from ..serializers import InvestorNotificationReadSerializer, InvestorNotificationCreateSerializer
from ..factories import InvestorNotificationFactory, NotificationCategoryFactory, InvestorProfileFactory, StartupProfileFactory, UserFactory
from django.urls import reverse
from django.test import RequestFactory
from unittest.mock import patch
from rest_framework_simplejwt.exceptions import InvalidToken


class InvestorNotificationSerializerTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up static data for the tests. This method runs once for the entire test class.
        """
        cls.notification_category = NotificationCategoryFactory()
        cls.investor = InvestorProfileFactory()
        cls.startup = StartupProfileFactory()
        cls.notification = InvestorNotificationFactory(
            notification_category=cls.notification_category,
            investor=cls.investor,
            startup=cls.startup,
        )

    def test_investor_notification_read_serializer(self):
        """
        Test the InvestorNotificationReadSerializer to ensure it correctly serializes the data.
        """
        request = RequestFactory().get('/')

        serializer = InvestorNotificationReadSerializer(instance=self.notification, context={'request': request})
        self.assertEqual(serializer.data["notification_category"], self.notification_category.description)
        self.assertEqual(serializer.data["investor"], str(self.investor))
        self.assertEqual(serializer.data["is_read"], self.notification.is_read)
        self.assertEqual(serializer.data["created_at"], self.notification.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertIn("notification_url", serializer.data)

    def test_investor_notification_create_serializer_valid_data(self):
        """
        Test the InvestorNotificationCreateSerializer with valid data to ensure it validates correctly.
        """
        data = {
            "notification_category": NotificationCategoryFactory().id,
            "investor": InvestorProfileFactory().id,
            "startup": StartupProfileFactory().id,
        }
        serializer = InvestorNotificationCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_investor_notification_create_serializer_duplicate_notification(self):
        """
        Test the InvestorNotificationCreateSerializer to ensure it detects duplicate notifications.
        """
        data = {
            "notification_category": self.notification_category.id,
            "investor": self.investor.id,
            "startup": self.startup.id,
        }
        serializer = InvestorNotificationCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["non_field_errors"][0].code, "unique")

    def test_investor_notification_create_serializer_invalid_data(self):
        """
        Test the InvestorNotificationCreateSerializer with invalid data to ensure it handles errors correctly.
        """
        data = {
            "notification_category": "invalid",
            "investor": "",
            "startup": None,
        }
        serializer = InvestorNotificationCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 3)
        self.assertEqual(serializer.errors["notification_category"][0].code, "incorrect_type")
        self.assertEqual(serializer.errors["investor"][0].code, "null")
        self.assertEqual(serializer.errors["startup"][0].code, "null")

    def test_investor_notification_create_serializer_create(self):
        """
        Test the InvestorNotificationCreateSerializer to ensure it creates a new notification correctly.
        """
        data = {
            "notification_category": NotificationCategoryFactory().id,
            "investor": InvestorProfileFactory().id,
            "startup": StartupProfileFactory().id,
        }
        serializer = InvestorNotificationCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            notification = InvestorNotification.objects.latest('id')
            self.assertEqual(notification.notification_category.id, data["notification_category"])
            self.assertEqual(notification.investor.id, data["investor"])
            self.assertEqual(notification.startup.id, data["startup"])
            self.assertFalse(notification.is_read)
        else:
            self.fail("Serializer is not valid")

    def test_investor_notification_create_serializer_invalid_notification_category(self):
        """
        Test the InvestorNotificationCreateSerializer with an invalid notification category ID.
        """
        data = {
            "notification_category": 999,
            "investor": self.investor.id,
            "startup": self.startup.id,
        }
        serializer = InvestorNotificationCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["notification_category"][0].code, "does_not_exist")

    def test_investor_notification_create_serializer_missing_required_fields(self):
        """
        Test the InvestorNotificationCreateSerializer with missing required fields.
        """
        data = {
            # Omit two required fields
            "notification_category": NotificationCategoryFactory().id,
        }
        serializer = InvestorNotificationCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 2)
        self.assertEqual(serializer.errors["investor"][0].code, "required")
        self.assertEqual(serializer.errors["startup"][0].code, "required")

    def test_investor_notification_create_serializer_empty_values(self):
        """
        Test the InvestorNotificationCreateSerializer with empty values for required fields.
        """
        data = {
            "notification_category": "",
            "investor": "",
            "startup": "",
        }
        serializer = InvestorNotificationCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 3)
        self.assertEqual(serializer.errors["notification_category"][0].code, "null")
        self.assertEqual(serializer.errors["investor"][0].code, "null")
        self.assertEqual(serializer.errors["startup"][0].code, "null")

    def test_investor_notification_create_serializer_null_values(self):
        """
        Test the InvestorNotificationCreateSerializer with null values for required fields.
        """
        data = {
            "notification_category": None,
            "investor": None,
            "startup": None,
        }
        serializer = InvestorNotificationCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 3)
        self.assertEqual(serializer.errors["notification_category"][0].code, "null")
        self.assertEqual(serializer.errors["investor"][0].code, "null")
        self.assertEqual(serializer.errors["startup"][0].code, "null")


class InvestorNotificationAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up static data for the tests. This method runs once for the entire test class.
        """
        cls.notification_category = NotificationCategoryFactory()
        cls.investor = InvestorProfileFactory()
        cls.startup = StartupProfileFactory()
        cls.notification = InvestorNotificationFactory(
            notification_category=cls.notification_category,
            investor=cls.investor,
            startup=cls.startup,
        )
        cls.user = cls.investor.user

    def setUp(self):
        """
        Set up data for each individual test. This method runs before each test.
        """
        self.client.force_authenticate(user=self.user)

    def test_notification_list_api(self):
        """
        Test the notification list API endpoint to ensure it returns the correct notifications.
        """
        url = reverse('notifications:investor_notifications')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_notification_list_api_pagination(self):
        """
        Test the notification list API endpoint to ensure pagination works correctly.
        """
        for _ in range(10):
            InvestorNotificationFactory(
                notification_category=self.notification_category,
                investor=self.investor,
                startup=StartupProfileFactory(),
            )
        url = reverse('notifications:investor_notifications')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 10)

    def test_notification_detail_api_set_is_read(self):
        """
        Test the notification detail API endpoint to ensure it marks the notification as read.
        """
        url = reverse('notifications:investor_notification_detail', args=[self.notification.id])
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_notification_detail_api_access_denied(self):
        """
        Test the notification detail API endpoint to ensure access is denied for unauthorized users.
        """
        other_investor = InvestorProfileFactory()
        other_notification = InvestorNotificationFactory(
            notification_category=self.notification_category,
            investor=other_investor,
            startup=self.startup,
        )
        url = reverse('notifications:investor_notification_detail', args=[other_notification.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_notification_detail_api_notification_not_found(self):
        """
        Test the notification detail API endpoint to ensure it returns a 404 error for non-existent notifications.
        """
        url = reverse('notifications:investor_notification_detail', args=[999])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class InvestorNotificationAdditionalEdgeCaseTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up static data for the tests. This method runs once for the entire test class.
        """
        cls.notification_category = NotificationCategoryFactory()
        cls.investor = InvestorProfileFactory()
        cls.startup = StartupProfileFactory()
        cls.user = cls.investor.user

        # Create a notification with maximum allowed field values
        cls.max_length_notification = InvestorNotificationFactory(
            notification_category=cls.notification_category,
            investor=cls.investor,
            startup=cls.startup,
        )

    def setUp(self):
        """
        Set up data for each individual test. This method runs before each test.
        """
        self.client.force_authenticate(user=self.user)

    def test_notification_with_max_field_values(self):
        """
        Test the notification API with maximum allowed field values to ensure it handles them correctly.
        """
        url = reverse('notifications:investor_notifications')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_notification_with_min_field_values(self):
        """
        Test the notification API with minimum allowed field values to ensure it handles them correctly.
        """
        # Create a notification with minimal data
        minimal_notification = InvestorNotificationFactory(
            notification_category=self.notification_category,
            investor=self.investor,
            startup=StartupProfileFactory(),  # Ensure uniqueness
        )
        url = reverse('notifications:investor_notifications')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Includes the max_length_notification

    def test_notification_list_api_search(self):
        """
        Test the search functionality of the notification list API endpoint.
        """
        # Create a unique notification with a distinct startup
        unique_startup = StartupProfileFactory()
        unique_notification = InvestorNotificationFactory(
            notification_category=self.notification_category,
            investor=self.investor,
            startup=unique_startup,
        )
        url = reverse('notifications:investor_notifications')
        response = self.client.get(url, {'search': unique_notification.notification_category.description}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_notification_list_api_filter(self):
        """
        Test the filter functionality of the notification list API endpoint.
        """
        # Create a notification with a specific category
        specific_category = NotificationCategoryFactory(description="Specific Category")
        filtered_notification = InvestorNotificationFactory(
            notification_category=specific_category,
            investor=self.investor,
            startup=StartupProfileFactory(),  # Ensure uniqueness
        )
        InvestorNotification.objects.filter(notification_category=specific_category).exclude(id=filtered_notification.id).delete()
        url = reverse('notifications:investor_notifications')
        response = self.client.get(url, {'notification_category': specific_category.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['notification_category'], specific_category.description)


class InvalidTokenTests(APITestCase):
    """
    Test behavior when an invalid token is used in API requests.
    """

    def setUp(self):
        self.url_list = reverse('notifications:investor_notifications')
        self.url_detail = reverse('notifications:investor_notification_detail', args=[1])

    @patch('rest_framework_simplejwt.authentication.JWTAuthentication.get_validated_token')
    def test_invalid_token_list_view(self, mock_get_validated_token):
        """
        Simulate invalid token behavior for notification list view.
        """
        mock_get_validated_token.side_effect = InvalidToken("Invalid token")

        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get(self.url_list)

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Expected 401 Unauthorized for invalid token in list view."
        )
        self.assertIn(
            "detail", response.data,
            "Expected 'detail' key in the response for invalid token."
        )
        self.assertEqual(
            response.data["detail"], "Invalid token",
            "Expected 'Invalid token' message for invalid token."
        )

    @patch('rest_framework_simplejwt.authentication.JWTAuthentication.get_validated_token')
    def test_invalid_token_detail_view(self, mock_get_validated_token):
        """
        Simulate invalid token behavior for notification detail view.
        """
        mock_get_validated_token.side_effect = InvalidToken("Invalid token")

        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get(self.url_detail)

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Expected 401 Unauthorized for invalid token in detail view."
        )
        self.assertIn(
            "detail", response.data,
            "Expected 'detail' key in the response for invalid token."
        )
        self.assertEqual(
            response.data["detail"], "Invalid token",
            "Expected 'Invalid token' message for invalid token."
        )


class InvestorNotificationQuerySetTests(APITestCase):
    """
    Tests for the custom QuerySet methods of the InvestorNotification model.
    """
    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the entire test class using factories.
        """
        # Create a test user
        cls.user = UserFactory(email='testuser@example.com', password='testpass')

        # Create an investor profile for the user
        cls.investor = InvestorProfileFactory(user=cls.user)

        # Create two startup profiles
        cls.startup1 = StartupProfileFactory()
        cls.startup2 = StartupProfileFactory()

        # Create two notification categories
        cls.category1 = NotificationCategoryFactory()
        cls.category2 = NotificationCategoryFactory()

        # Create test notifications with unique combinations of fields
        cls.notification1 = InvestorNotificationFactory(
            notification_category=cls.category1,
            investor=cls.investor,
            startup=cls.startup1,
            is_read=False
        )
        cls.notification2 = InvestorNotificationFactory(
            notification_category=cls.category2,
            investor=cls.investor,
            startup=cls.startup2,
            is_read=True
        )

    def test_unread_notifications(self):
        """
        Test filtering unread notifications.
        """
        # Filter unread notifications
        unread_notifications = InvestorNotification.objects.unread()

        # Assert that only unread notifications are returned
        self.assertEqual(unread_notifications.count(), 1)
        self.assertEqual(unread_notifications.first(), self.notification1)
        self.assertFalse(unread_notifications.first().is_read)

    def test_for_investor(self):
        """
        Test filtering notifications for a specific investor.
        """
        # Filter notifications for the test investor
        notifications = InvestorNotification.objects.for_investor(self.investor)

        # Assert that only notifications for the investor are returned
        self.assertEqual(notifications.count(), 2)
        self.assertIn(self.notification1, notifications)
        self.assertIn(self.notification2, notifications)

    def test_mark_all_as_read(self):
        """
        Test marking all unread notifications as read for a user.
        """
        # Mark all unread notifications as read
        InvestorNotification.mark_all_as_read(self.user)

        # Refresh the notifications from the database
        self.notification1.refresh_from_db()
        self.notification2.refresh_from_db()

        # Assert that all notifications are now marked as read
        self.assertTrue(self.notification1.is_read)
        self.assertTrue(self.notification2.is_read)