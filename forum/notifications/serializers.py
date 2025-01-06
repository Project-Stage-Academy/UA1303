from rest_framework import serializers
from .models import NotificationMethod, NotificationCategory, NotificationPreference, NotificationForUpdates


class NotificationMethodSerializer(serializers.ModelSerializer):
    """Serializer for the NotificationMethod model."""

    class Meta:
        model = NotificationMethod
        fields = ["id", "name", "description"]


class NotificationCategorySerializer(serializers.ModelSerializer):
    """Serializer for the NotificationCategory model."""

    class Meta:
        model = NotificationCategory
        fields = ["id", "name", "description"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for the NotificationPreferences model."""

    allowed_notification_categories = serializers.SerializerMethodField()
    allowed_notification_methods = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = NotificationPreference
        fields = [
            "user",
            "allowed_notification_methods",
            "allowed_notification_categories",
        ]

    def get_allowed_notification_methods(self, obj):
        notification_methods = obj.allowed_notification_methods.all()
        return NotificationMethodSerializer(notification_methods, many=True).data

    def get_allowed_notification_categories(self, obj):
        notification_categories = obj.allowed_notification_categories.all()
        return NotificationCategorySerializer(notification_categories, many=True).data


class NotificationPreferenceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating the NotificationCategory model."""

    allowed_notification_methods = serializers.PrimaryKeyRelatedField(
        many=True, queryset=NotificationMethod.objects.all()
    )

    allowed_notification_categories = serializers.PrimaryKeyRelatedField(
        many=True, queryset=NotificationCategory.objects.all()
    )

    class Meta:
        model = NotificationPreference
        fields = ["allowed_notification_methods", "allowed_notification_categories"]


class NotificationForUpdatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationForUpdates
        fields = ['id', 'message', 'notification_type', 'startup_profile', 'project', 'created_at', 'is_read']