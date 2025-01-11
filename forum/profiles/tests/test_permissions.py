from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import Role
import factory
from rest_framework.test import APITestCase


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
        role = factory.Faker('random_element', elements=[Role.STARTUP, Role.INVESTOR, Role.BOTH, Role.UNASSIGNED])

    def setUp(self):
        """
        Set up users with different roles using factory
        """
        # Create users with different roles
        self.admin_user = self.UserFactory(role=Role.STARTUP)
        self.regular_user = self.UserFactory(role=Role.INVESTOR)

        # Generate JWT tokens for both users
        self.admin_token = self.get_jwt_token(self.admin_user)
        self.regular_token = self.get_jwt_token(self.regular_user)

        # Initialize API client
        self.client = APIClient()

    def get_jwt_token(self, user):
        """
        Helper function to generate a JWT token for a given user
        """
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return access_token

    def test_admin_access(self):
        """
        Test that an admin user can access an endpoint that requires admin role
        """
        url = reverse('some_admin_protected_endpoint')

        # Admin user accesses the endpoint
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_access(self):
        """
        Test that a regular user cannot access an endpoint that requires admin role
        """
        url = reverse('some_admin_protected_endpoint')

        # Regular user accesses the endpoint
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.regular_token)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_with_invalid_token(self):
        """
        Test that an invalid token is rejected
        """
        url = reverse('some_admin_protected_endpoint')

        # Using an invalid token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalid_token')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_role_based_permissions(self):
        """
        Test that access is based on the user's role
        """
        url = reverse('some_role_based_endpoint')

        # Admin user accesses role-based endpoint
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Regular user tries to access role-based endpoint
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.regular_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_role_alignment(self):
        """
        Test the role alignment logic for user and token role
        """
        # Token role should align with user role
        self.assertTrue(Role.has_role(self.admin_user.role, Role.STARTUP))
        self.assertTrue(Role.token_role_aligns(self.admin_user.role, Role.STARTUP))

        # Testing non-aligning roles
        self.assertFalse(Role.has_role(self.regular_user.role, Role.STARTUP))
        self.assertFalse(Role.token_role_aligns(self.regular_user.role, Role.STARTUP))
