import factory
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import Role


class RolePermissionTests(APITestCase):
    """
    Test class for role-based permissions
    """

    class UserFactory(factory.django.DjangoModelFactory):
        """
        Factory to create users with different roles
        """

        class Meta:
            model = get_user_model()

        email = factory.Faker('email')
        password = factory.Faker('password')
        first_name = factory.Faker('first_name')
        last_name = factory.Faker('last_name')
        role = factory.Faker('random_element', elements=[Role.STARTUP, Role.INVESTOR])

    def setUp(self):
        """
        Set up users with different roles using factory
        """
        self.startup_user = self.UserFactory(role=Role.STARTUP)
        self.investor_user = self.UserFactory(role=Role.INVESTOR)

        self.startup_token = self.get_jwt_token(self.startup_user)
        self.investor_token = self.get_jwt_token(self.investor_user)

        self.client = APIClient()

    def tearDown(self):
        """
        Clean up created data after tests
        """
        self.startup_user.delete()
        self.investor_user.delete()

    def get_jwt_token(self, user):
        """
        Helper function to generate a JWT token for a given user
        """
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return access_token

    def test_startup_access_startup_profile(self):
        """
        Test that a startup user can access startup profile endpoint
        """
        url = reverse('startup-profile-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.startup_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_investor_access_startup_profile(self):
        """
        Test that an investor user cannot access startup profile endpoint
        """
        url = reverse('startup-profile-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_investor_access_investor_profile(self):
        """
        Test that an investor user can access investor profile endpoint
        """
        url = reverse('investor-profile-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.investor_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_startup_access_investor_profile(self):
        """
        Test that a startup user cannot access investor profile endpoint
        """
        url = reverse('investor-profile-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.startup_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_with_invalid_token(self):
        """
        Test that an invalid token is rejected
        """
        url = reverse('startup-profile-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalid_token')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
