from rest_framework import status
from rest_framework.test import APITestCase
from notifications.factories import InvestorProfileFactory, StartupProfileFactory
from django.urls import reverse

from notifications.tests.test_notificationpreference import generate_auth_header


class NotificationsAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Create investors and startups
        cls.investor_1 = InvestorProfileFactory()
        cls.investor_2 = InvestorProfileFactory()
        cls.startup_1 = StartupProfileFactory()
        cls.startup_2 = StartupProfileFactory()

        # Generate authorization headers
        cls.auth_header_startup_1 = generate_auth_header(cls.startup_1.user, 1)
        cls.auth_header_startup_2 = generate_auth_header(cls.startup_2.user, 1)
        cls.auth_header_investor_1 = generate_auth_header(cls.investor_1.user, 2)
        cls.auth_header_investor_2 = generate_auth_header(cls.investor_2.user, 2)

    def test_viewed_startups_list(self):
        """
        Test retrieving the list of startups viewed by an investor.
        """
        # Investor views two startups
        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_2.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        # Check the viewing history
        url = reverse('profiles:startup-profile-viewed-startups')
        response = self.client.get(url, **self.auth_header_investor_1)
        
        self.assertEqual(len(response.json()), 2)
        self.assertNotEqual(response.json(), [])
        self.assertIn('startup_id', response.json()[0])

    def test_clear_viewed_startups_history(self):
        """
        Test clearing the history of startups viewed by an investor.
        """
        # Investor views two startups
        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_2.pk})
        response = self.client.get(url, **self.auth_header_investor_1)
        
        # Clear the viewing history
        url = reverse('profiles:startup-profile-clear-viewed')
        response = self.client.delete(url, **self.auth_header_investor_1)
        
        # Check that the history is empty
        url = reverse('profiles:startup-profile-viewed-startups')
        response = self.client.get(url, **self.auth_header_investor_1)
        
        self.assertEqual(response.json(), [])
        
    def test_viewed_startups_serializer_fields(self):
        """
        Test checking serializer fields for viewed startups.
        """
        # Investor views a startup
        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        # Retrieve the list of viewed startups
        url = reverse('profiles:startup-profile-viewed-startups')
        response = self.client.get(url, **self.auth_header_investor_1)

        # Check the presence and absence of specific fields
        self.assertIn('startup_id', response.json()[0])
        self.assertIn('company_name', response.json()[0])
        self.assertIn('viewed_at', response.json()[0])
        self.assertNotIn('industry', response.json()[0])
        self.assertNotIn('size', response.json()[0])
        self.assertNotIn('country', response.json()[0])
        self.assertNotIn('city', response.json()[0])

    def test_no_duplicate_viewed_startups(self):
        """
        Test uniqueness of viewed startups in the history.
        """
        # Investor views the same startup twice
        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_investor_1)

        # Check that there is only one entry for this startup in the history
        url = reverse('profiles:startup-profile-viewed-startups')
        response = self.client.get(url, **self.auth_header_investor_1)

        self.assertEqual(len(response.json()), 1)

    def test_investor_access_control(self):
        """
        Test access control for viewing history available only to investors.
        """
        # Request made by a startup user who is not an investor
        url = reverse('profiles:startup-profile-detail', kwargs={'pk': self.startup_1.pk})
        response = self.client.get(url, **self.auth_header_startup_2)

        # Check the error message for unauthorized access
        url = reverse('profiles:startup-profile-viewed-startups')
        response = self.client.get(url, **self.auth_header_startup_2)

        self.assertEqual(response.json()['detail'], 'No InvestorProfile matches the given query.')

