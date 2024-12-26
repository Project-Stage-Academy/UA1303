from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import render
from requests import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.contrib.auth import get_user_model
from rest_framework import status

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
        serializer.save(sender=self.request.user)

class MessageHistoryView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['conversation_id']
        return Message.objects.filter(room_id=room_id).order_by('timestamp')


