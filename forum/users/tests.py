from django.forms import ValidationError
from django.test import TestCase
from .validators import SpecialCharacterPasswordValidator
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser
from django.urls import reverse


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


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth:user-register')
        self.valid_payload = self.create_payload()

        self.existing_user = CustomUser.objects.create_user(
            email="existing@example.com",
            password="ExistingPassword123!",
            first_name="Existing",
            last_name="User",
            role=0,
        )

    def create_payload(self, email="default@example.com", password="StrongPassword123!", **kwargs):
        base_payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": email,
            "password": password,
        }
        base_payload.update(kwargs)
        return base_payload

    def test_valid_user_registration(self):
        response = self.client.post(self.register_url, data=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 2)
        self.assertEqual(response.data["email"], self.valid_payload["email"])

    def test_missing_required_fields(self):
        incomplete_payload = {"first_name": "John"}
        response = self.client.post(self.register_url, data=incomplete_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)

    def test_invalid_email(self):
        invalid_payload = self.create_payload(email="not-an-email")
        response = self.client.post(self.register_url, data=invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_duplicate_email_registration(self):
        duplicate_payload = self.create_payload(email=self.existing_user.email)
        response = self.client.post(self.register_url, data=duplicate_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_very_long_names(self):
        long_name = 'A' * 50   #max length 30
        payload = self.create_payload(first_name=long_name, last_name=long_name)
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)

    def test_weak_passwords(self):
        payload = self.create_payload(password="12345")  # Weak password
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_missing_optional_fields(self):
        payload = self.create_payload(role=None)
        del payload["role"]  #remove the optional field
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('email', response.data)