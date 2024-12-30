from rest_framework import serializers
from users.serializers import CustomUserSerializer
from .models import Room, Message


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name", "online"]
        extra_kwargs = {"name": {"required": False}}

    def create(self, validated_data):
        participants = validated_data.pop("online", [])
        if len(participants) != 2:
            raise serializers.ValidationError(
                "A conversation must have exactly two participants."
            )
        room_name = f"room_{participants[0].user_id}_{participants[1].user_id}"
        room = Room.objects.create(name=room_name, **validated_data)
        room.online.set(participants)
        return room


class MessageSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "room", "user", "content", "timestamp"]
        read_only_fields = ["user", "timestamp"]
        extra_kwargs = {"content": {"required": True}, "user": {"required": True}}

    def validate(self, attrs):
        user = self.context["request"].user
        room = attrs.get("room")

        if not room.online.filter(user_id=user.user_id).exists():
            raise serializers.ValidationError("You are not a member of this room.")
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate_content(self, value):
        if len(value) > 512:
            raise serializers.ValidationError(
                "Content must have less than 512 characters."
            )
        return value
