from rest_framework import serializers
from .models import ChatRoom, Message

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'participants']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'text', 'timestamp']
        read_only_fields = ['sender', 'timestamp']