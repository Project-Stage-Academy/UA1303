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

    def validate_email(self, value):
        if self.instance:
            if self.instance.email != value:
                if InvestorProfile.objects.filter(email=value).exists():
                    raise serializers.ValidationError(
                        "Investor with this email already exists."
                    )
        else:
            if InvestorProfile.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "Investor with this email already exists."
                )
        return value

    def validate_account_balance(self, value):
        if value > 1000000000.00 or value < 0:
            raise serializers.ValidationError(
                "Account balance have incorrect value."
            )
        return value

    def validate_user(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist.")
        return value
