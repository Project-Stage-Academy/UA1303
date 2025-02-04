from rest_framework import serializers
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, Role
import logging
from django.db import transaction
from notifications.models import(
    NotificationCategory,
    NotificationMethod,
    NotificationPreference
)

logger = logging.getLogger(__name__)

def create_default_notification_preferences(user):
    try:
        with transaction.atomic():
            default_methods = NotificationMethod.objects.filter(name__in=["email", "in_app"])
            default_categories = NotificationCategory.objects.filter(name__in=["follow", "profile_update", "new_project"])
            notification_preference = NotificationPreference.objects.create(user=user)
            notification_preference.allowed_notification_methods.set(default_methods)
            notification_preference.allowed_notification_categories.set(default_categories)
            logger.info(f"Default notification preferences set to the user.")
    except Exception as e:
        logger.error(f"Error creating default notification preferences: {e}")


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is not registered.")
        return value


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "user_id",
            "first_name",
            "last_name",
            "email",
            "user_phone",
            "role",
            "title",
            "password",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("user_id", "created_at", "updated_at")
        extra_kwargs = {"password": {"write_only": True}}
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        instance = CustomUser.objects.create(**validated_data)
        if password:
            self.validate_password(password)
            instance.set_password(password)
        instance.save()

        create_default_notification_preferences(instance)
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            self.validate_password(password)
            if not instance.check_password(password):
                instance.set_password(password)
        instance.save()
        return instance

    def validate_email(self, value):
        if self.instance:
            if self.instance.email != value:
                if CustomUser.objects.filter(email=value).exists():
                    raise serializers.ValidationError(
                        "A user with this email already exists."
                    )
        else:
            if CustomUser.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "A user with this email already exists."
                )

        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_role(self, value):
        valid_roles = [choice[0] for choice in CustomUser.ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError("Invalid role.")
        return value


VALID_TOKEN_ROLES = [Role.STARTUP, Role.INVESTOR]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    role = serializers.ChoiceField(choices=[(role.value, role.name.lower()) for role in VALID_TOKEN_ROLES])
    
    def validate(self, attrs):
        data = super().validate(attrs)

        request = self.context.get('request')
        role = request.data.get('role')

        if role is None:
            raise exceptions.ValidationError({"role": "This field is required."})
        
        try:
            role = int(role)
            if role not in [role.value for role in VALID_TOKEN_ROLES]:
                raise ValueError
        except (ValueError, TypeError):
            raise exceptions.ValidationError({"role": "Invalid role specified."})

        refresh = self.get_token(self.user)
        refresh['role'] = role

        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)

        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate(self, data):
        request = self.context.get('request')
        auth_header = request.headers.get('Authorization', '')
        access_token = auth_header.split()[1]
        refresh_token = data.get('refresh')
        
        try:
            decoded_access_token = AccessToken(access_token)
            user_id_from_access = decoded_access_token['user_id']
        except Exception as e:
            raise serializers.ValidationError({"access token error": str(e)})

        try:
            decoded_refresh_token = RefreshToken(refresh_token)
            user_id_from_refresh = decoded_refresh_token['user_id']
        except Exception as e:
            raise serializers.ValidationError({"refresh token error": str(e)})

        if user_id_from_access != user_id_from_refresh:
            raise serializers.ValidationError({"error": "User ID mismatch between tokens."})

        return data


class RoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[(role.value, role.name.lower()) for role in VALID_TOKEN_ROLES])

    def validate(self, attrs):
        role = attrs.get("role")
        if role is None:
            raise exceptions.ValidationError({"role": "This field is required."})
        return attrs


class GithubAccessTokenSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, allow_blank=False, error_messages={
        'required': 'The code field is required.',
        'blank': 'The code field cannot be blank.'
    })
    redirect_url = serializers.CharField(required=True, allow_blank=False, error_messages={
        'required': 'The redirect_url field is required.',
        'blank': 'The redirect_url field cannot be blank.'
    })

    def validate_code(self, value):
        """Validation for the `code` field."""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("The code field cannot be empty or contain only whitespace.")
        return value

    def validate_redirect_url(self, value):
        """Validation for the `redirect_url` field."""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("The redirect_url field cannot be empty or contain only whitespace.")
        if not value.startswith("http://") and not value.startswith("https://"):
            raise serializers.ValidationError("The redirect_url must be a valid URL starting with http:// or https://.")
        return value
