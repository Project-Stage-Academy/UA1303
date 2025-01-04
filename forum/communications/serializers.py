from rest_framework import serializers
from rest_framework_mongoengine import (
    serializers as mongo_serializers,
)
from .models import Room, Message


class MessageSerializer(serializers.Serializer):
    user = serializers.IntegerField()
    content = serializers.CharField(max_length=512)

    def create(self, validated_data):
        return Message(**validated_data)


class RoomSerializer(mongo_serializers.DocumentSerializer):
    messages = serializers.ListField(
        child=MessageSerializer(),
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = Room
        fields = ["id", "name", "participants", "messages"]
        extra_kwargs = {"name": {"required": False}}

    def validate_participants(self, value):
        current_user = self.context["request"].user
        if current_user.user_id not in value:
            raise serializers.ValidationError(
                "You must include yourself as a participant."
            )
        return value
