from unittest.mock import Mock
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import Role
from users.serializers import CustomTokenObtainPairSerializer

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
        with self.assertRaises(ValidationError) as exc:
            serializer.validate(request_data)

        self.assertIn("role", exc.exception.detail)
        self.assertEqual(exc.exception.detail["role"], "Invalid role specified.")

    def test_missing_role(self):
        """Test that a missing role raises a ValidationError."""
        request_data = {"email": self.user.email, "password": "securepassword"}  # No role provided
        context = {"request": self._get_mock_request(request_data)}

        serializer = CustomTokenObtainPairSerializer(context=context)
        with self.assertRaises(ValidationError) as exc:
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
