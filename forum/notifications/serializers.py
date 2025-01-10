from rest_framework import serializers
from .models import NotificationMethod, NotificationCategory, NotificationPreference
from .models import StartUpNotification, InvestorProfile, StartupProfile


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

class StartUpNotificationReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading startup notifications and updating the 'is_read' status.

    This serializer provides read-only access to the notification's details,
    including the notification category, investor, and creation date.
    The 'is_read' field can be updated using this serializer, allowing clients to mark notifications as read.

    Attributes:
        notification_category (str): The category of notification (read-only).
        investor (str): The investor related to the notification (read-only).
        is_read (bool): Indicates whether the notification has been read (can be updated).
        created_at (datetime): The date and time the notification was created (read-only).
    """

    notification_category = serializers.StringRelatedField(source='notification_category.description', read_only=True)
    investor = serializers.StringRelatedField(read_only=True)

    notification_url = serializers.HyperlinkedIdentityField(
        view_name='notifications:notification_detail',  
        lookup_field='id'  
    )

    class Meta:
        model = StartUpNotification
        fields = ['notification_category', 'investor', 'is_read', 'created_at', 'notification_url']
        read_only_fields = ['notification_category', 'investor', 'created_at', 'notification_url']

class StartUpNotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating startup notifications.
    """
    notification_category = serializers.PrimaryKeyRelatedField(
        queryset=NotificationCategory.objects.all()
    )
    investor = serializers.PrimaryKeyRelatedField(
        queryset=InvestorProfile.objects.all()
    )
    startup = serializers.PrimaryKeyRelatedField(
        queryset=StartupProfile.objects.all()
    )

    class Meta:
        model = StartUpNotification
        fields = ['notification_category', 'investor', 'startup', 'is_read']

    def create(self, validated_data):
        return StartUpNotification.objects.create(**validated_data)
    
    def validate(self, data):
        if StartUpNotification.objects.filter(
            notification_category=data['notification_category'],
            investor=data['investor'],
            startup=data['startup']
        ).exists():
            raise serializers.ValidationError("This notification already exists.")
        return data