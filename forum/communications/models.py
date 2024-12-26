from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoom(models.Model):
    participants = models.ManyToManyField(User, related_name='chat_rooms')

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
