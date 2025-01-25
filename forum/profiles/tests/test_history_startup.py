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
        cls.startup_1 = StartupProfileFactory()
        cls.startup_2 = StartupProfileFactory()

        cls.auth_header_startup_1 = generate_auth_header(cls.startup_1.user, 1)
        cls.auth_header_startup_2 = generate_auth_header(cls.startup_2.user, 1)
        cls.auth_header_investor_1 = generate_auth_header(cls.investor_1.user, 2)
        cls.auth_header_investor_2 = generate_auth_header(cls.investor_2.user, 2)

    def test_retrieve_history_list(self):
        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_2.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        url = reverse('profiles:startup-profile-viewed-startups')
        response = self.client.get(url, **self.auth_header_investor_1)
        
        self.assertEqual(len(response.json()), 2)
        self.assertNotEqual(response.json(), [])
        self.assertIn('startup_id', response.json()[0])

    def test_delete_history(self):
        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_2.pk})
        response = self.client.get(url, **self.auth_header_investor_1)
        
        url = reverse('profiles:startup-profile-clear-viewed')
        response = self.client.delete(url, **self.auth_header_investor_1)
        
        url = reverse('profiles:startup-profile-viewed-startups')
        response = self.client.get(url, **self.auth_header_investor_1)
        
        self.assertEqual(response.json(), [])
        
    def test_serializer_field(self):
        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        url = reverse('profiles:startup-profile-viewed-startups')
        response = self.client.get(url, **self.auth_header_investor_1)

        self.assertIn('startup_id', response.json()[0])
        self.assertIn('company_name', response.json()[0])
        self.assertIn('viewed_at', response.json()[0])
        self.assertNotIn('industry', response.json()[0])
        self.assertNotIn('size', response.json()[0])
        self.assertNotIn('country', response.json()[0])
        self.assertNotIn('city', response.json()[0])

    def test_unique_constraint(self):
        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        url = reverse('profiles:startup-profile-viewed-startups')
        response = self.client.get(url, **self.auth_header_investor_1)

        self.assertEqual(len(response.json()), 1)

    def test_access_control_for_investor(self):
        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_startup_2)

        url = reverse('profiles:startup-profile-viewed-startups')
        response = self.client.get(url, **self.auth_header_startup_2)
        print(response.json())

