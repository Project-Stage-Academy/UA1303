from rest_framework import serializers
from .models import NotificationType, NotificationPreference
from rest_framework import serializers
from .models import StartUpNotification, InvestorProfile, StartupProfile
from rest_framework.response import Response
from rest_framework import status



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

class StartUpNotificationReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading startup notifications and updating the 'is_read' status.

    This serializer provides read-only access to the notification's details,
    including the notification type, investor, and creation date.
    The 'is_read' field can be updated using this serializer, allowing clients to mark notifications as read.

    Attributes:
        notification_type (str): The type of notification (read-only).
        investor (str): The investor related to the notification (read-only).
        is_read (bool): Indicates whether the notification has been read (can be updated).
        created_at (datetime): The date and time the notification was created (read-only).
    """

    notification_type = serializers.StringRelatedField(source='notification_type.name', read_only=True)
    investor = serializers.StringRelatedField(read_only=True)

    notification_url = serializers.HyperlinkedIdentityField(
        view_name='notifications:notification_detail',  
        lookup_field='id'  
    )

    class Meta:
        model = StartUpNotification
        fields = ['notification_type', 'investor', 'is_read', 'created_at', 'notification_url']
        read_only_fields = ['notification_type', 'investor', 'created_at', 'notification_url']

class StartUpNotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating startup notifications.
    """
    notification_type = serializers.PrimaryKeyRelatedField(
        queryset=NotificationType.objects.all()
    )
    investor = serializers.PrimaryKeyRelatedField(
        queryset=InvestorProfile.objects.all()
    )
    startup = serializers.PrimaryKeyRelatedField(
        queryset=StartupProfile.objects.all()
    )

    class Meta:
        model = StartUpNotification
        fields = ['notification_type', 'investor', 'startup', 'is_read']

    def create(self, validated_data):
        return StartUpNotification.objects.create(**validated_data)
    
    def validate(self, data):
        if StartUpNotification.objects.filter(
            notification_type=data['notification_type'],
            investor=data['investor'],
            startup=data['startup']
        ).exists():
            raise serializers.ValidationError("This notification already exists.")
        return data