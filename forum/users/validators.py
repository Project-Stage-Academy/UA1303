from django.core.exceptions import ValidationError
from rest_framework import serializers


class SpecialCharacterPasswordValidator:
    special_characters = "!@#$%^&*()_+"

    def validate(self, password, user=None):
        errors = []
        if not any(char in self.special_characters for char in password):
            errors.append(f"at least one special character ({self.special_characters})")
        if not any(char.isupper() for char in password):
            errors.append("at least one uppercase letter")
        if not any(char.islower() for char in password):
            errors.append("at least one uppercase letter")
        if errors:
            raise ValidationError(f"The password must contain {', '.join(errors)}.")

    def get_help_text(self):
        return (
            "Your password must contain at least one special character (!@#$%^&*()_+) "
            "and one uppercase letter."
        )
