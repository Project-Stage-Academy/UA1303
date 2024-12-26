from unittest.mock import Mock
from django.forms import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.exceptions import PermissionDenied
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .permissions import IsInvestor, IsStartup
from .models import Role
from .validators import SpecialCharacterPasswordValidator
from .serializers import CustomTokenObtainPairSerializer


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


User = get_user_model()


class TestCustomTokenObtainPairSerializer(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="securepassword",
            role=Role.INVESTOR.value  # Assign a default role
        )

    def test_valid_role(self):
        """Test that a valid role is added to the token payload."""
        request_data = {"email": self.user.email, "password": "securepassword", "role": Role.STARTUP.value}
        context = {"request": self._get_mock_request(request_data)}

        serializer = CustomTokenObtainPairSerializer(context=context)
        validated_data = serializer.validate(request_data)

        # Extract refresh token
        refresh_token = RefreshToken(validated_data["refresh"])

        self.assertEqual(refresh_token["role"], Role.STARTUP.value)

    def test_invalid_role(self):
        """Test that an invalid role raises a ValidationError."""
        request_data = {"email": self.user.email, "password": "securepassword", "role": 9999}  # Invalid role
        context = {"request": self._get_mock_request(request_data)}

        serializer = CustomTokenObtainPairSerializer(context=context)
        with self.assertRaises(exceptions.ValidationError) as exc:
            serializer.validate(request_data)

        self.assertIn("role", exc.exception.detail)
        self.assertEqual(exc.exception.detail["role"], "Invalid role specified.")

    def test_missing_role(self):
        """Test that a missing role raises a ValidationError."""
        request_data = {"email": self.user.email, "password": "securepassword"}  # No role provided
        context = {"request": self._get_mock_request(request_data)}

        serializer = CustomTokenObtainPairSerializer(context=context)
        with self.assertRaises(exceptions.ValidationError) as exc:
            serializer.validate(request_data)

        self.assertIn("role", exc.exception.detail)
        self.assertEqual(exc.exception.detail["role"], "This field is required.")


    def test_role_added_to_access_token(self):
        """Test that the role is correctly added to the access token."""
        request_data = {"email": self.user.email, "password": "securepassword", "role": Role.INVESTOR.value}
        context = {"request": self._get_mock_request(request_data)}

        serializer = CustomTokenObtainPairSerializer(context=context)
        validated_data = serializer.validate(request_data)

        # Extract access token
        access_token = RefreshToken(validated_data["refresh"]).access_token

        self.assertEqual(access_token["role"], Role.INVESTOR.value)
    
    def test_token_issued_for_role_user_does_not_possess(self):
        """Test that a token is issued even when the user requests a role they don't possess."""
        # Define test cases: (current_user_role, requested_role)
        test_cases = [
            (Role.UNASSIGNED, Role.INVESTOR),  # Unassigned user requests investor token
            (Role.UNASSIGNED, Role.STARTUP),  # Unassigned user requests startup token
            (Role.INVESTOR, Role.STARTUP),    # Investor user requests startup token
            (Role.STARTUP, Role.INVESTOR),    # Startup user requests investor token
        ]

        for user_role, requested_role in test_cases:
            with self.subTest(current_role=user_role, requested_role=requested_role):
                # Update user's database role
                self.user.role = user_role.value
                self.user.save()

                # Request token for a different role
                request_data = {
                    "email": self.user.email,
                    "password": "securepassword",
                    "role": requested_role.value,
                }
                context = {"request": self._get_mock_request(request_data)}

                serializer = CustomTokenObtainPairSerializer(context=context)
                validated_data = serializer.validate(request_data)

                # Extract the issued token
                refresh_token = RefreshToken(validated_data["refresh"])

                # Assert the token is issued successfully
                self.assertEqual(refresh_token["role"], requested_role.value)
                self.assertNotEqual(refresh_token["role"], user_role.value)  # Ensure it reflects the requested role

    
    def test_empty_request_payload(self):
        """Test that an empty request payload raises a ValidationError."""
        request_data = {}
        context = {"request": self._get_mock_request(request_data)}

        serializer = CustomTokenObtainPairSerializer(data=request_data, context=context)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertIn("password", serializer.errors)
        self.assertIn("role", serializer.errors)

    def _get_mock_request(self, data):
        """Helper method to create a mock request object with given data."""
        mock_request = Mock()
        mock_request.data = data
        return mock_request
