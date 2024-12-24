from unittest.mock import Mock
from django.forms import ValidationError
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import AccessToken
from .permissions import IsInvestor, IsStartup
from .models import Role
from .validators import SpecialCharacterPasswordValidator


class CustomUserValidatorTest(TestCase):

    def setUp(self):
        self.validator = SpecialCharacterPasswordValidator()
        self.valid_password_cases = [
            "StrongP@ssw0rd",
            "Another#Pass123",
            "Passw0rd!",
            "1234Abc#1234",
            "Complex$Password1",
            "ValidPassword2024!",
        ]

        self.invalid_password_cases = [
            "password",
            "12345678",
            "PASSWORD",
            "short",
            "nouppercase123@",
            "NOLOWERCASE123@",
            "NoSpecialChar123",
            " space in pass ",
            "repeated!!repeated!!",
        ]

    def test_valid_passwords(self):
        for password in self.valid_password_cases:
            with self.subTest(password=password):
                try:
                    self.validator.validate(password)
                except ValidationError:
                    self.fail(
                        f"Valid password '{password}' raised ValidationError unexpectedly."
                    )

    def test_invalid_passwords(self):
        for invalid_password in self.invalid_password_cases:
            with self.subTest(invalid_password=invalid_password):
                with self.assertRaises(ValidationError) as context:
                    self.validator.validate(invalid_password)
                error_message = str(context.exception)
                self.assertTrue(
                    any(
                        error in error_message
                        for error in [
                            "The password must contain at least one special character",
                            "The password must contain at least one uppercase letter",
                            "The password must contain at least one lowercase letter",
                        ]
                    ),
                    f"Invalid password '{invalid_password}' did not raise the correct error message. Error was: {error_message}",
                )

    def test_edge_case_passwords(self):
        edge_cases = [
            "!A1",  
            "A" * 50 + "@1", 
            "!!@#$%^&*()_+", 
        ]
        for password in edge_cases:
            with self.subTest(password=password):
                try:
                    self.validator.validate(password)
                except ValidationError as e:
                    self.assertRaises(ValidationError)
                    self.assertTrue(e.messages, "ValidationError must contain error messages.")

    def test_empty_and_none_passwords(self):
        invalid_cases = ["", None]
        for password in invalid_cases:
            with self.subTest(password=password):
                with self.assertRaises(ValidationError):
                    self.validator.validate(password)


class TestBaseRolePermission(APITestCase):
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

        permission = IsInvestor()
        has_permission = permission.has_permission(self.mock_request, self.mock_view)

        self.assertFalse(has_permission)

    def test_request_user_missing_role_attribute(self):
        """Test that requests without a user role attribute are denied."""
        del self.mock_user.role  # Simulate user missing the `role` attribute

        permission = IsInvestor()
        with self.assertRaises(PermissionDenied):
            permission.has_permission(self.mock_request, self.mock_view)

    def test_correct_role_grants_access(self):
        """Test that users with the correct role are granted access."""
        self.mock_user.role = Role.INVESTOR.value

        permission = IsInvestor()
        has_permission = permission.has_permission(self.mock_request, self.mock_view)

        self.assertTrue(has_permission)

    def test_incorrect_role_denies_access(self):
        """Test that users with an incorrect role are denied access."""
        self.mock_user.role = Role.STARTUP.value

        permission = IsInvestor()
        has_permission = permission.has_permission(self.mock_request, self.mock_view)

        self.assertFalse(has_permission)

    def test_invalid_auth_type(self):
        """Test that invalid authentication raises PermissionDenied."""
        self.mock_request.auth = None  # Simulate no authentication

        permission = IsInvestor()
        with self.assertRaises(PermissionDenied):
            permission.has_permission(self.mock_request, self.mock_view)