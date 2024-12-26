from rest_framework import serializers
from .models import NotificationType, NotificationPreference
from django.contrib.auth.models import User


class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = ['id', 'name', 'description']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for reading user's notification preferences.
    """
    allowed_notification_types = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = NotificationPreference
        fields = ['user', 'allowed_notification_types']

    def get_allowed_notification_types(self, obj):
        notification_types = obj.allowed_notification_types.all()
        return NotificationTypeSerializer(notification_types, many=True).data


class NotificationPreferenceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user's notification preferences.
    """
    allowed_notification_types = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=NotificationType.objects.all()
    )

    class Meta:
        model = NotificationPreference
        fields = ['allowed_notification_types']
