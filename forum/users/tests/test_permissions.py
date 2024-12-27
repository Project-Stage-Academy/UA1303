from unittest.mock import Mock
from rest_framework.test import APITestCase
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import AccessToken
from users.models import Role
from users.permissions import IsInvestor, IsStartup


class TestBaseRolePermission(APITestCase):
    def _setup_mock_token_and_user(self, role: Role):
        """Helper to set up mock token and user with the specified role.
        Takes user role value (e.g. `Role.STARTUP.value`)"""
        self.mock_user.role = role.value
        self.mock_token.get = Mock(return_value=role.value)
    
    def setUp(self):
        # Create mock user and token
        self.mock_user = Mock()
        self.mock_user.is_authenticated = True

        self.mock_token = Mock(spec=AccessToken)
        self.mock_token.get = Mock(return_value=Role.INVESTOR.value)

        self.mock_request = Mock()
        self.mock_request.auth = self.mock_token
        self.mock_request.user = self.mock_user
        self.mock_view = Mock()

    def test_user_not_authenticated(self):
        """Test that unauthenticated users are denied access."""
        self.mock_user.is_authenticated = False

        for permission_class in [IsInvestor, IsStartup]:
            with self.subTest(permission=permission_class):
                permission = permission_class()
                has_permission = permission.has_permission(self.mock_request, self.mock_view)
                self.assertFalse(has_permission)

    def test_request_user_missing_role_attribute(self):
        """Test that requests without a user role attribute are denied."""
        del self.mock_user.role  # Simulate user missing the `role` attribute

        for permission_class in [IsInvestor, IsStartup]:
            with self.subTest(permission=permission_class):
                permission = permission_class()
                with self.assertRaises(PermissionDenied) as exc:
                    permission.has_permission(self.mock_request, self.mock_view)
                
                self.assertEqual(exc.exception.detail, "User instance doesn't have role attribute")
    
    def test_token_missing_role_attribute(self):
        """Test that a token missing the 'role' attribute raises PermissionDenied."""
        # Setup mock token without the 'role' attribute
        self.mock_token.get = Mock(return_value=None)  # Simulate no 'role' attribute
        self.mock_request.auth = self.mock_token

        for permission_class in [IsInvestor, IsStartup]:
            with self.subTest(permission=permission_class):
                permission = permission_class()
                with self.assertRaises(PermissionDenied) as exc:
                    permission.has_permission(self.mock_request, self.mock_view)

                self.assertEqual(exc.exception.detail, "Token doesn't have role attribute")


    def test_correct_role_grants_access(self):
        """Test that users with the correct role are granted access."""
        # Iterate over each role and its corresponding permission
        test_cases = [
            (Role.INVESTOR, IsInvestor),
            (Role.STARTUP, IsStartup),
        ]
        for user_role, permission_class in test_cases:
            with self.subTest(role=user_role, permission=permission_class):
                self._setup_mock_token_and_user(user_role)

                permission = permission_class()
                has_permission = permission.has_permission(self.mock_request, self.mock_view)
                self.assertTrue(has_permission)
    
    def test_unassigned_role_denies_access(self):
        """Test that users with the Role.UNASSIGNED role are denied access."""
        self._setup_mock_token_and_user(Role.UNASSIGNED)

        for permission_class in [IsInvestor, IsStartup]:
            with self.subTest(permission=permission_class):
                permission = permission_class()
                has_permission = permission.has_permission(self.mock_request, self.mock_view)
                self.assertFalse(has_permission)

    def test_incorrect_role_denies_access(self):
        """Test that users with an incorrect role are denied access."""
        test_cases = [
            (Role.STARTUP, IsInvestor),  # Startup user, investor permission
            (Role.INVESTOR, IsStartup),  # Investor user, startup permission
        ]
        for user_role, permission_class in test_cases:
            with self.subTest(role=user_role, permission=permission_class):
                self._setup_mock_token_and_user(user_role)

                permission = permission_class()
                has_permission = permission.has_permission(self.mock_request, self.mock_view)
                self.assertFalse(has_permission)

    def test_invalid_auth_type(self):
        """Test that invalid authentication raises PermissionDenied."""
        self.mock_request.auth = None  # Simulate no authentication

        for permission_class in [IsInvestor, IsStartup]:
            with self.subTest(permission=permission_class):
                permission = permission_class()
                with self.assertRaises(PermissionDenied) as exc:
                    permission.has_permission(self.mock_request, self.mock_view)
                
                self.assertEqual(exc.exception.detail, "Authentication failed: missing or invalid JWT.")