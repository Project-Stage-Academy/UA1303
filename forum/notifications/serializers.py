from rest_framework import serializers
from .models import NotificationType, NotificationPreference
from django.contrib.auth.models import User


class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = ['id', 'name', 'description']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Показує ім'я користувача
    allowed_notification_types = NotificationTypeSerializer(many=True)  # Вбудовані серіалізатори для типів сповіщень

    class Meta:
        model = NotificationPreference
        fields = ['user', 'allowed_notification_types']
