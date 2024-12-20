from django.forms import ValidationError
from django.test import TestCase
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
