from rest_framework import serializers
from .models import CustomUser
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


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

    def validate_first_name(self, value):
        if len(value) > 30:
            raise serializers.ValidationError("First name must not exceed 50 characters.")
        return value

    def validate_last_name(self, value):
        if len(value) > 30:
            raise serializers.ValidationError("Last name must not exceed 50 characters.")
        return value