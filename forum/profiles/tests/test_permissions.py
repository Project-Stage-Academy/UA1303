import factory
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from profiles.models import InvestorProfile, StartupProfile
from users.models import Role


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory to create users with roles
    """

    class Meta:
        model = get_user_model()

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    role = factory.Iterator([Role.INVESTOR, Role.STARTUP, Role.BOTH])


class InvestorProfileFactory(factory.django.DjangoModelFactory):
    """
    Factory to create InvestorProfile linked to User
    """

    class Meta:
        model = InvestorProfile

    user = factory.SubFactory(UserFactory)
    investment_amount = factory.Faker('random_number')
    bio = factory.Faker('text')


class StartupProfileFactory(factory.django.DjangoModelFactory):
    """
    Factory to create StartupProfile linked to User
    """

    class Meta:
        model = StartupProfile

    user = factory.SubFactory(UserFactory)
    company_name = factory.Faker('company')
    industry = factory.Faker('word')
    country = factory.Faker('country')
    city = factory.Faker('city')
    size = factory.Faker('random_int')


class RolePermissionTests(APITestCase):
    """
    Test permissions for different roles
    """

    def setUp(self):
        """
        Create test users with different roles using factories
        """
        self.investor_user = UserFactory(role=Role.INVESTOR)
        self.investor_profile = InvestorProfileFactory(user=self.investor_user)

        self.startup_user = UserFactory(role=Role.STARTUP)
        self.startup_profile = StartupProfileFactory(user=self.startup_user)

        self.both_user = UserFactory(role=Role.BOTH)
        self.startup_profile_both = StartupProfileFactory(user=self.both_user)
        self.investor_profile_both = InvestorProfileFactory(user=self.both_user)

        self.investor_token = self.get_token(self.investor_user)
        self.startup_token = self.get_token(self.startup_user)
        self.both_token = self.get_token(self.both_user)

    def get_token(self, user):
        """
        Generate and return a token for the user
        """

        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_investor_access_to_investor_view(self):
        """
        Test that an INVESTOR can access the Investor view
        """

        url = '/api/investor-profiles/'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_startup_access_to_startup_view(self):
        """
        Test that a STARTUP can access the Startup profile view
        """

        url = '/api/startup-profiles/'  # Example URL for startup profiles
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.startup_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_both_user_access_to_investor_view(self):
        """
        Test that a BOTH user can access the Investor view
        """

        url = '/api/investor-profiles/'  # Example URL for investor profiles
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.both_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_both_user_access_to_startup_view(self):
        """
        Test that a BOTH user can access the Startup profile view
        """

        url = '/api/startup-profiles/'  # Example URL for startup profiles
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.both_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_investor_access_to_investor_view(self):
        """
        Test that a user without INVESTOR role cannot access the Investor view
        """

        url = '/api/investor-profiles/'  # Example URL for investor profiles
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.startup_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_startup_access_to_startup_view(self):
        """
        Test that a user without STARTUP role cannot access the Startup profile view
        """

        url = '/api/startup-profiles/'  # Example URL for startup profiles
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
