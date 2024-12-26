from rest_framework import serializers
from .models import NotificationType, NotificationCategory, NotificationPreference
from users.models import CustomUser


class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = ['id', 'name', 'description']


class NotificationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationCategory
        fields = ['id', 'name', 'description']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for reading user's notification preferences.
    """
    allowed_notification_categories = serializers.SerializerMethodField()
    allowed_notification_types = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = NotificationPreference
        fields = [
            'user',
            'allowed_notification_types',
            'allowed_notification_categories'
        ]

    def get_allowed_notification_types(self, obj):
        notification_types = obj.allowed_notification_types.all()
        return NotificationTypeSerializer(notification_types, many=True).data
    
    def get_allowed_notification_categories(self, obj):
        notification_categories = obj.allowed_notification_categories.all()
        return NotificationCategorySerializer(notification_categories, many=True).data


class NotificationPreferenceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user's notification preferences.
    """
    allowed_notification_types = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=NotificationType.objects.all()
    )

    allowed_notification_categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=NotificationCategory.objects.all()
    )

    class Meta:
        model = NotificationPreference
        fields = [
            'allowed_notification_types',
            'allowed_notification_categories'
        ]
