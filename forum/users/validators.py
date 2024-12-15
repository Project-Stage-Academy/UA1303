from django.core.exceptions import ValidationError
from rest_framework import serializers


class SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not any(char in "!@#$%^&*()_+" for char in password):
            raise serializers.ValidationError(
                {
                    "password": "The password must contain at least one special character (!@#$%^&*()_+)."
                }
            )
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError(
                {"password": "The password must contain at least one upper character"}
            )

    def get_help_text(self):
        return (
            "Your password must contain at least one special character (!@#$%^&*()_+) "
            "and one uppercase letter."
        )
