from django.urls import path
from .views import CreateConversationView, AddMessageView, MessageHistoryView

from . import views

app_name = "communications"

urlpatterns = [
    path("", views.index, name="index"),
    path("room/<str:room_name>/", views.room, name="room"),
    path(
        "conversations/", CreateConversationView.as_view(), name="create_conversation"
    ),
    path("<str:room_id>/messages/", AddMessageView.as_view(), name="send_message"),
    path(
        "conversations/<str:room_id>/messages/",
        MessageHistoryView.as_view(),
        name="message_history",
    ),
]
