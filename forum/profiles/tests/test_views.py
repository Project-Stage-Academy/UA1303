from rest_framework import status
from rest_framework.test import APITestCase
from notifications.factories import InvestorProfileFactory, StartupProfileFactory
from django.urls import reverse

from notifications.tests.test_notificationpreference import generate_auth_header


class NotificationsAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.investor_1 = InvestorProfileFactory()
        cls.investor_2 = InvestorProfileFactory()
        cls.startup = StartupProfileFactory()

        cls.auth_header_startup = generate_auth_header(cls.startup.user, 1)
        cls.auth_header_investor_1 = generate_auth_header(cls.investor_1.user, 2)
        cls.auth_header_investor_2 = generate_auth_header(cls.investor_2.user, 2)

    def test_basic(self):
        url = reverse('profiles:startups-view-startup', kwargs={'pk': self.startup.pk})
        response = self.client.get(url, **self.auth_header_investor_1)