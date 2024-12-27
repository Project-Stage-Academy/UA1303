from rest_framework import serializers
from .models import Room, Message


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "online"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "room", "user", "content", "timestamp"]
        read_only_fields = ["user", "timestamp"]
