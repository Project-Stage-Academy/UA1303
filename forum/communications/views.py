from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.contrib.auth import get_user_model
from .permissions import IsParticipant
from django.core.exceptions import PermissionDenied
from .paginations import MessagePagination

User = get_user_model()


def index(request):
    return render(request, "communications/index.html")


def room(request, room_name):
    return render(request, "communications/room.html", {"room_name": room_name})


class CreateConversationView(generics.CreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        room = serializer.validated_data["room"]
        if self.request.user not in room.online.all():
            raise PermissionDenied("You are not a participant of this conversation.")
        serializer.save(user=self.request.user)


class MessageHistoryView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    pagination_class = MessagePagination

    def get_queryset(self):
        room_id = self.kwargs["conversation_id"]
        return Message.objects.filter(room_id=room_id).order_by("timestamp")
