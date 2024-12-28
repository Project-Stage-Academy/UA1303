from rest_framework import serializers
from users.serializers import CustomUserSerializer
from .models import Room, Message


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "online"]


class MessageSerializer(serializers.ModelSerializer):
    user=CustomUserSerializer()
    class Meta:
        model = Message
        fields = ["id", "room", "user", "content", "timestamp"]
        read_only_fields = ["user", "timestamp"]
