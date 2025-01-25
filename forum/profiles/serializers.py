from django.contrib.auth import get_user_model
from projects.serializers import ProjectSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import StartupProfile, InvestorProfile, ViewedStratups

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


class StartupProfileSerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = StartupProfile
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        if user.is_anonymous:
            raise ValidationError('You must be logged in.')
        if self.context['request'].method == 'POST' and StartupProfile.objects.filter(user=user).exists():
            raise ValidationError(
                "You cannot create multiple startup profiles. Each user is limited to one startup profile.")
        return data


class PublicStartupProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = StartupProfile
        fields = [
            'id',
            'company_name',
            'industry',
            'country',
            'city',
            'description',
        ]


class ViewedStratupReadSerializer(serializers.ModelSerializer):
    
    startup_id= serializers.StringRelatedField(source='startup.id', read_only=True)
    company_name= serializers.StringRelatedField(source='startup.company_name', read_only=True)

    
    class Meta:
        model = ViewedStratups
        fields = [
            'startup_id',
            'company_name',
            'viewed_at'
        ]


class ViewedStratupCreateSerializer(serializers.ModelSerializer):
    
    investor = serializers.PrimaryKeyRelatedField(
        queryset=InvestorProfile.objects.all()
    )
    startup = serializers.PrimaryKeyRelatedField(
        queryset=StartupProfile.objects.all()
    )

    class Meta:
        model = ViewedStratups
        fields = ['investor', 'startup', 'viewed_at']

    def create(self, validated_data):
        return ViewedStratups.objects.create(**validated_data)