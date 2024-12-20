from rest_framework import serializers
from .models import InvestorProfile
from django.core.validators import validate_email


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
