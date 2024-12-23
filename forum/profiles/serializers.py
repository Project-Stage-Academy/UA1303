from rest_framework import serializers
from .models import InvestorProfile
from django.core.validators import validate_email
from django.contrib.auth import get_user_model

User = get_user_model()


class InvestorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorProfile
        fields = [
            "id",
            "user",
            "country",
            "city",
            "zip_code",
            "address",
            "phone",
            "email",
            "account_balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]
        extra_kwargs = {
            "phone": {"required": False},
        }

    def validate_email(self, value):
        if (
            InvestorProfile.objects.filter(email=value)
            .exclude(pk=self.instance.pk if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError(
                "Investor with this email already exists."
            )
        return value

    def validate_account_balance(self, value):
        if value > 9999999999999.99 or value < 0:
            raise serializers.ValidationError(
                "Account balance have incorrect value.It required to be positive and lower than 9999999999999.99"
            )
        return value

    def validate_zip_code(self, value):
        if not any(element.isdigit() for element in value):
            raise serializers.ValidationError("Non-numeric zip code.")
        return value
