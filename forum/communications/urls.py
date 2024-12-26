from django.urls import path
from .views import CreateConversationView, SendMessageView, MessageHistoryView

from . import views

app_name = "communications"

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path('conversations/', CreateConversationView.as_view(), name='create_conversation'),
    path('messages/', SendMessageView.as_view(), name='send_message'),
    path('conversations/<int:conversation_id>/messages/', MessageHistoryView.as_view(), name='message_history'),
]
