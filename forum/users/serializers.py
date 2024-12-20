from rest_framework import serializers
from .models import CustomUser, Role
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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
    def validate(self, attrs):
        data = super().validate(attrs)

        request = self.context.get('request')
        role = request.data.get('role')

        if role is None:
            raise serializers.ValidationError({"role": "This field is required."})
        
        try:
            role = int(role)
            if role not in [role.value for role in VALID_TOKEN_ROLES]:
                raise ValueError
        except (ValueError, TypeError):
            raise serializers.ValidationError({"role": "Invalid role specified."})

        refresh = self.get_token(self.user)
        refresh['role'] = role

        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)

        return data
