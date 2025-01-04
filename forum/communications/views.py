from django.forms import ValidationError
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Room, Message
from .serializers import RoomSerializer
from .permissions import IsParticipant
from .paginations import MessagePagination
from bson import ObjectId
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ValidationError
from .serializers import MessageSerializer


User = get_user_model()


def index(request):
    return render(request, "communications/index.html")


def room(request, room_name):
    return render(request, "communications/room.html", {"room_name": room_name})


class CreateConversationView(generics.CreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        participants = serializer.validated_data.get("participants", [])

        if len(participants) != 2:
            raise ValidationError("A conversation must have exactly two participants.")

        existing_room = Room.objects(participants__all=participants).count() > 0
        if existing_room:
            raise ValidationError("This conversation already exists.")

        name = f"room_{participants[0]}_{participants[1]}"

        serializer.save(name=name)


class AddMessageView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsParticipant,
    ]

    def post(self, request, room_id):
        try:
            room_object_id = ObjectId(room_id)
        except Exception as e:
            raise ValidationError("Invalid room ID format.")

        try:
            room = Room.objects.get(id=room_object_id)
        except Room.DoesNotExist:
            raise NotFound("Room not found.")

        message_serializer = MessageSerializer(data=request.data)
        if not message_serializer.is_valid():
            raise ValidationError(message_serializer.errors)

        message = message_serializer.save()

        if not hasattr(room, "messages"):
            room.messages = []
        room.messages.append(message)

        room.save()

        return Response(
            {"status": "Message added successfully."}, status=status.HTTP_201_CREATED
        )


class MessageHistoryView(APIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    pagination_class = MessagePagination

    def get(self, request, room_id):
        try:
            room_id = ObjectId(room_id)
        except Exception as err:
            raise ValidationError({"detail": "Invalid room ID format."})

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise NotFound({"detail": "Room not found."})

        messages = room.messages

        paginator = self.pagination_class()
        paginated_messages = paginator.paginate_queryset(messages, request)

        serializer = self.serializer_class(paginated_messages, many=True)
        return paginator.get_paginated_response(serializer.data)
