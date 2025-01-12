from rest_framework import status
from rest_framework.test import APITestCase
from ..models import InvestorNotification
from ..serializers import InvestorNotificationReadSerializer, InvestorNotificationCreateSerializer
from ..factories import InvestorNotificationFactory, NotificationCategoryFactory, InvestorProfileFactory, StartupProfileFactory
from django.urls import reverse
from django.test import RequestFactory


class InvestorNotificationSerializerTests(APITestCase):
    def setUp(self):
        self.notification_category = NotificationCategoryFactory()
        self.investor = InvestorProfileFactory()
        self.startup = StartupProfileFactory()
        self.notification = InvestorNotificationFactory(
            notification_category=self.notification_category,
            investor=self.investor,
            startup=self.startup,
        )

    def test_investor_notification_read_serializer(self):
        request = RequestFactory().get('/')

        serializer = InvestorNotificationReadSerializer(instance=self.notification, context={'request': request})
        self.assertEqual(serializer.data["notification_category"], self.notification_category.description)
        self.assertEqual(serializer.data["investor"], str(self.investor))
        self.assertEqual(serializer.data["is_read"], self.notification.is_read)
        self.assertEqual(serializer.data["created_at"], self.notification.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertIn("notification_url", serializer.data)

    def test_investor_notification_create_serializer_valid_data(self):
        data = {
            "notification_category": NotificationCategoryFactory().id,
            "investor": InvestorProfileFactory().id,
            "startup": StartupProfileFactory().id,
        }
        serializer = InvestorNotificationCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_investor_notification_create_serializer_duplicate_notification(self):
        data = {
            "notification_category": self.notification_category.id,
            "investor": self.investor.id,
            "startup": self.startup.id,
        }
        serializer = InvestorNotificationCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["non_field_errors"][0].code, "unique")

    def test_investor_notification_create_serializer_invalid_data(self):
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
        data = {
            "notification_category": 999,
            "investor": self.investor.id,
            "startup": self.startup.id,
        }
        serializer = InvestorNotificationCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["notification_category"][0].code, "does_not_exist")

    def test_investor_notification_create_serializer_missing_required_fields(self):
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
    def setUp(self):
        self.notification_category = NotificationCategoryFactory()
        self.investor = InvestorProfileFactory()
        self.startup = StartupProfileFactory()
        self.notification = InvestorNotificationFactory(
            notification_category=self.notification_category,
            investor=self.investor,
            startup=self.startup,
        )
        self.user = self.investor.user
        self.client.force_authenticate(user=self.user)

    def test_notification_list_api(self):
        url = reverse('notifications:investor_notifications')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_notification_list_api_pagination(self):
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
        url = reverse('notifications:investor_notification_detail', args=[self.notification.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_notification_detail_api_access_denied(self):
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
        url = reverse('notifications:investor_notification_detail', args=[999])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)